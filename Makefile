.PHONY: help sync test lint typecheck dev inspector install-skills clean

help:
	@echo "jiphyeonjeon-agent dev targets:"
	@echo "  make sync           - uv sync (install deps)"
	@echo "  make test           - pytest unit tests"
	@echo "  make lint           - ruff check + format check"
	@echo "  make typecheck      - mypy strict"
	@echo "  make dev            - run server with MCP Inspector UI"
	@echo "  make install-skills - copy skills/ into ~/.claude/skills/"
	@echo "  make clean          - remove caches"

sync:
	uv sync

test:
	uv run pytest tests/unit/ -v

lint:
	uv run ruff check src tests
	uv run ruff format --check src tests

typecheck:
	uv run mypy src

dev:
	@test -n "$$JIPHYEONJEON_TOKEN" || (echo "Set JIPHYEONJEON_TOKEN first"; exit 1)
	uv run mcp dev src/jiphyeonjeon_mcp/server.py

install-skills:
	@mkdir -p $$HOME/.claude/skills
	@for f in skills/*.md; do \
		name=$$(basename $$f .md); \
		target=$$HOME/.claude/skills/$$name; \
		mkdir -p $$target; \
		cp $$f $$target/SKILL.md; \
		echo "installed: $$target/SKILL.md"; \
	done

clean:
	rm -rf .pytest_cache .ruff_cache .mypy_cache dist build
	find . -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null || true
