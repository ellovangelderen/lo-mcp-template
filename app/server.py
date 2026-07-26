"""Personal context MCP server (template).

Serves your personal context profile — the "how to work with me" operating
manual — as MCP resources and tools, so every AI surface (Claude Code, chat
apps, scheduled agents) loads the same single source of truth.

Boundary: identity and working style only. Keep live operational data (tasks,
metrics, budgets) in the systems that own it; this server answers "who am I
and how do I work", nothing else.

Run locally over stdio (simplest, for Claude Code on the same machine):

    MCP_TRANSPORT=stdio python -m app.server
    # register: claude mcp add my-profile --env MCP_TRANSPORT=stdio -- python -m app.server

Or over HTTP (for remote surfaces; put real access control in front):

    MCP_HOST=127.0.0.1 python -m app.server
    # listens on http://127.0.0.1:8080/mcp, health at /health
"""
import os
from pathlib import Path

from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

# Profile markdown lives at repo-root/profile/, one file per section.
PROFILE_DIR = Path(__file__).resolve().parent.parent / "profile"

# Order matters: identity first — it is the file an agent reads if it can
# read only one.
PROFILE_FILES = [
    ("identity", "Who you are in one page."),
    ("entities", "Your tracks (work, side projects, roles) and the separations between them."),
    ("communication-style", "How you write and want things written."),
    ("rules-and-constraints", "Hard rules any agent must respect."),
    ("routines-and-cues", "Standing routines and the cues that trigger them."),
    ("interface-guide", "What each connected system is for, and what is off-limits."),
    ("pointers", "Where live data and systems of record actually live."),
]

mcp = FastMCP(
    name="personal-context",
    instructions=(
        "Personal context profile: the how-to-work-with-me operating manual. "
        "Read get_profile for the full context, or get_section for one part. "
        "Identity and working style only; live operational data lives "
        "elsewhere."
    ),
)


def _read(name: str) -> str:
    path = PROFILE_DIR / f"{name}.md"
    if not path.exists():
        return f"(missing: {name}.md)"
    return path.read_text(encoding="utf-8")


# Expose each profile section as an MCP resource.
def _make_resource(name: str, description: str):
    @mcp.resource(f"profile://{name}", name=name, description=description)
    def _resource() -> str:
        return _read(name)

    return _resource


for _name, _description in PROFILE_FILES:
    _make_resource(_name, _description)


@mcp.tool
def get_profile() -> str:
    """Return the full context profile, all sections concatenated in load order."""
    parts = []
    for name, _ in PROFILE_FILES:
        parts.append(f"# === {name} ===\n\n{_read(name)}")
    return "\n\n".join(parts)


@mcp.tool
def get_section(section: str) -> str:
    """Return one profile section by name.

    Valid sections: identity, entities, communication-style,
    rules-and-constraints, routines-and-cues, interface-guide, pointers.
    """
    valid = {n for n, _ in PROFILE_FILES}
    if section not in valid:
        return f"Unknown section '{section}'. Valid: {', '.join(sorted(valid))}"
    return _read(section)


@mcp.tool
def list_sections() -> str:
    """List the available profile sections with a one-line description each."""
    return "\n".join(f"- {n}: {d}" for n, d in PROFILE_FILES)


@mcp.custom_route("/health", methods=["GET"])
async def health(request: Request) -> JSONResponse:
    missing = [n for n, _ in PROFILE_FILES if not (PROFILE_DIR / f"{n}.md").exists()]
    ok = not missing
    return JSONResponse(
        {"status": "ok" if ok else "degraded", "missing_sections": missing},
        status_code=200 if ok else 503,
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"},
    )


def main() -> None:
    if os.environ.get("MCP_TRANSPORT", "http") == "stdio":
        mcp.run(transport="stdio")
        return
    mcp.run(
        transport="http",
        host=os.environ.get("MCP_HOST", "0.0.0.0"),
        port=int(os.environ.get("PORT") or os.environ.get("MCP_PORT", "8080")),
        path="/mcp",
    )


if __name__ == "__main__":
    main()
