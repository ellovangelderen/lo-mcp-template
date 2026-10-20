# Personal context MCP — template

Serve your personal "how to work with me" manual as an MCP server, so every
AI surface you use (Claude Code, chat apps, scheduled agents) loads the same
single source of truth about who you are and how you work.

This is a **template**: the profile sections here are placeholders with
writing guidance. Fill them with your own content and you have your own
personal-context server. It contains no real profile data and is deliberately
independent from the author's actual profile.

## The pattern

Whoever works with multiple AI surfaces ends up explaining themselves over
and over — and the explanations drift apart. The fix:

1. **One canonical profile**: identity, tracks, communication style, hard
   rules, routines, interfaces, pointers. Markdown, one file per section, in
   `profile/`.
2. **A tiny MCP server** that serves it: `get_profile` (everything),
   `get_section` (one part), `list_sections`, plus each section as an MCP
   resource.
3. **Every surface starts by loading it.** Interactive session or headless
   nightly run: same manual, same rules.
4. Changing an agreement is **one edit** in the canon, not a hunt across
   seven system prompts. Bonus: a periodic drift-check comparing all places
   where your context lives against this canon.

Two design rules that keep it healthy:

- **Identity only, no live data.** Tasks, metrics and budgets live in the
  systems that own them; the `pointers` section says where. Operational data
  in a profile goes stale by lunchtime.
- **Identity first.** The section order is deliberate: if an agent reads only
  one file, it should be `identity.md`.

## Quick start

Requires Python 3.10+.

```bash
pip install -r requirements.txt

# Local, stdio (simplest — Claude Code on the same machine):
claude mcp add my-profile --env MCP_TRANSPORT=stdio -- python -m app.server

# Or as an HTTP server (remote surfaces):
python -m app.server        # http://127.0.0.1:8080/mcp, health at /health
```

Then fill in the seven files under `profile/` — each explains what belongs in
it — and ask your agent to `get_profile`.

**If you expose this over HTTP: put real access control in front** (an
authenticating proxy or tunnel). Your profile is personal by definition; the
server itself does no auth, which is why it listens on localhost unless a
hosting platform sets `PORT` or you set `MCP_HOST=0.0.0.0` yourself.

`requirements.txt` pins an exact version on purpose: that lets Dependabot and
other scanners match it against known vulnerabilities. Bump it deliberately.

## Background

Why this pattern exists and how it behaves in daily use:
[the write-up in werken-met-cos](https://github.com/ellovangelderen/werken-met-cos/blob/main/agent-tips/lo-principaal-mcp.md)
(Dutch). Built on Anthropic's
[Model Context Protocol](https://modelcontextprotocol.io).

## License

MIT — see [LICENSE](LICENSE).
