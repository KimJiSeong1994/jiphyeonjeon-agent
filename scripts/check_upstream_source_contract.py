"""Extract the MCP-facing contract from PaperReview FastAPI source and validate it.

This is the nightly fallback while the hosted service does not expose OpenAPI.
It intentionally uses only Python's AST and never imports the backend, whose app
startup has heavyweight runtime dependencies and side effects.
"""

from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jiphyeonjeon_mcp.openapi_contract import validate_openapi_contract


@dataclass(frozen=True)
class SourceOperation:
    file: str
    router_name: str
    method: str
    route: str
    model: str | None = None
    response_model: bool = False


OPERATIONS: tuple[SourceOperation, ...] = (
    SourceOperation("api_server.py", "app", "get", "/api/version", "VersionResponse", True),
    SourceOperation("routers/search.py", "router", "post", "/search", "SearchRequest"),
    SourceOperation("routers/papers.py", "router", "get", "/papers/{paper_id}"),
    SourceOperation("routers/reviews.py", "router", "post", "/deep-review", "DeepReviewRequest"),
    SourceOperation("routers/reviews.py", "router", "get", "/deep-review/status/{session_id}"),
    SourceOperation("routers/reviews.py", "router", "get", "/deep-review/report/{session_id}"),
    SourceOperation("routers/bookmarks.py", "router", "get", "/bookmarks"),
    SourceOperation(
        "routers/bookmarks.py",
        "router",
        "post",
        "/bookmarks/from-paper",
        "BookmarkFromPaperRequest",
    ),
    SourceOperation("routers/bookmarks.py", "router", "delete", "/bookmarks/{bookmark_id}"),
    SourceOperation(
        "routers/exploration.py",
        "router",
        "post",
        "/bookmarks/{bookmark_id}/citation-tree",
        "CitationTreeRequest",
    ),
    SourceOperation(
        "routers/curriculum.py",
        "router",
        "post",
        "/curricula/generate",
        "CurriculumGenerateRequest",
    ),
    SourceOperation(
        "routers/autofigure.py",
        "router",
        "post",
        "/method-to-svg",
        "MethodToSvgRequest",
    ),
    SourceOperation("routers/blog.py", "router", "post", "/posts", "PostCreateRequest"),
    SourceOperation("routers/blog.py", "router", "put", "/posts/{post_id}", "PostUpdateRequest"),
)


def _call_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _router_prefix(tree: ast.Module, router_name: str) -> str:
    if router_name == "app":
        return ""
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        assigned_to_router = any(
            isinstance(target, ast.Name) and target.id == router_name for target in node.targets
        )
        if not assigned_to_router:
            continue
        if not isinstance(node.value, ast.Call) or _call_name(node.value.func) != "APIRouter":
            continue
        for keyword in node.value.keywords:
            if keyword.arg == "prefix" and isinstance(keyword.value, ast.Constant):
                return str(keyword.value.value)
    raise ValueError(f"could not find {router_name}=APIRouter(prefix=...) assignment")


def _decorated_function(
    tree: ast.Module, operation: SourceOperation
) -> ast.FunctionDef | ast.AsyncFunctionDef | None:
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call) or not isinstance(decorator.func, ast.Attribute):
                continue
            owner = decorator.func.value
            if not isinstance(owner, ast.Name) or owner.id != operation.router_name:
                continue
            if decorator.func.attr != operation.method or not decorator.args:
                continue
            route_arg = decorator.args[0]
            if isinstance(route_arg, ast.Constant) and route_arg.value == operation.route:
                return node
    return None


def _model_fields(tree: ast.Module, name: str) -> set[str]:
    for node in tree.body:
        if not isinstance(node, ast.ClassDef) or node.name != name:
            continue
        return {
            field.target.id
            for field in node.body
            if isinstance(field, ast.AnnAssign) and isinstance(field.target, ast.Name)
        }
    raise ValueError(f"could not find model {name}")


def _annotation_names(function: ast.FunctionDef | ast.AsyncFunctionDef) -> set[str]:
    names: set[str] = set()
    for argument in (*function.args.posonlyargs, *function.args.args, *function.args.kwonlyargs):
        if argument.annotation is not None:
            names.update(
                node.id for node in ast.walk(argument.annotation) if isinstance(node, ast.Name)
            )
    return names


def _has_response_model(
    function: ast.FunctionDef | ast.AsyncFunctionDef, operation: SourceOperation
) -> bool:
    for decorator in function.decorator_list:
        if not isinstance(decorator, ast.Call):
            continue
        for keyword in decorator.keywords:
            if keyword.arg == "response_model" and _call_name(keyword.value) == operation.model:
                return True
    return False


def extract_contract(root: Path) -> tuple[dict[str, Any], list[str]]:
    document: dict[str, Any] = {
        "openapi": "3.1.0",
        "paths": {},
        "components": {"schemas": {}},
    }
    errors: list[str] = []
    trees: dict[str, ast.Module] = {}

    for operation in OPERATIONS:
        path = root / operation.file
        try:
            tree = trees.get(operation.file)
            if tree is None:
                tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
                trees[operation.file] = tree
            prefix = _router_prefix(tree, operation.router_name)
        except (OSError, SyntaxError, ValueError) as exc:
            errors.append(f"{operation.file}: {exc}")
            continue

        function = _decorated_function(tree, operation)
        full_path = f"{prefix}{operation.route}"
        if function is None:
            errors.append(f"missing source route: {operation.method.upper()} {full_path}")
            continue

        operation_document: dict[str, Any] = {}
        if operation.model is not None:
            try:
                fields = _model_fields(tree, operation.model)
            except ValueError as exc:
                errors.append(f"{operation.file}: {exc}")
                continue
            schema_name = operation.model
            document["components"]["schemas"][schema_name] = {
                "type": "object",
                "properties": {field: {} for field in sorted(fields)},
            }
            schema_ref = {"$ref": f"#/components/schemas/{schema_name}"}
            if operation.response_model:
                if not _has_response_model(function, operation):
                    errors.append(
                        f"GET {full_path} no longer declares response_model={schema_name}"
                    )
                operation_document["responses"] = {
                    "200": {"content": {"application/json": {"schema": schema_ref}}}
                }
            else:
                if schema_name not in _annotation_names(function):
                    errors.append(
                        f"{operation.method.upper()} {full_path} no longer accepts {schema_name}"
                    )
                operation_document["requestBody"] = {
                    "content": {"application/json": {"schema": schema_ref}}
                }
        document["paths"].setdefault(full_path, {})[operation.method] = operation_document
    return document, errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paperreview_root", type=Path)
    args = parser.parse_args()
    document, errors = extract_contract(args.paperreview_root)
    errors.extend(validate_openapi_contract(document))
    if errors:
        print("Upstream source contract drift detected:")
        for error in dict.fromkeys(errors):
            print(f"- {error}")
        return 1
    print("Upstream PaperReview source contract compatible")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
