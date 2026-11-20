---
name: channel-artifact
description: Builds an interactive HTML artifact backed by a Claude Code channel plugin. The user gets a localhost UI where they pin comments on the page or on data points; each pin reaches the live session as a channel notification, and Claude answers (queries MCPs, runs code) and updates the artifact in place. Works for any UI, such as dashboards, explorers, graph editors, kanban boards, map annotators or design canvases. Use when the user wants a persistent visual tool they can poke at and question over time, or says 'interactive artifact', 'pin comments', 'channel plugin', 'dashboard I can chat with', 'annotations Claude responds to', or mentions the fakechat pattern. Not for static charts or one-off plots.
---

# Channel artifact

Build any interactive HTML artifact served at `localhost:<PORT>` by a Bun-backed MCP channel plugin. The user pins comments on specific nodes OR anywhere on the page; each pin push-delivers to the live Claude session as a `notifications/claude/channel` event; Claude addresses the question and calls back via tool calls to update the artifact in place. Comments persist; addressed comments stay pinned with Claude's reply rendered beneath them; the UI updates live over WebSocket.

## Step 0: Interview the user first

Before scaffolding anything, ASK. This skill is domain-agnostic — the user's intent shapes everything downstream. Cover these with short, targeted questions:

- **What does the artifact show?** Dashboard with funnel data? Graph/network editor? Kanban board? Timeline? Map? Image annotator? Custom data viz?
- **Where does the data come from?** An MCP server (PostHog, Stripe, GitHub, Linear, Notion, etc.)? A local file? Generated on the fly? None yet (blank canvas)?
- **What are the "nodes" the user will comment on?** A funnel step? A graph vertex? A kanban card? A region of an image? Freeform anywhere on the page is always enabled — this is about *named* anchors.
- **What does Claude do when a comment arrives?** Query more data? Modify the artifact (e.g., rearrange nodes, add a new section)? Write a natural-language reply? All of the above?
- **Where should the plugin live?** Default: `tools/<plugin-name>/` in the current project. Alternatives: `~/tools/<plugin-name>/` for user-level, or inside an existing repo.
- **What's the plugin name?** Kebab-case, becomes the MCP server name and the channel source.
- **Any sensitive data to redact?** Revenue, PII, API keys — the UI should show them blurred (`class="redacted"`) or not at all.

Don't proceed until you have answers. If the user says "just vibe with me and build something simple", pick sensible defaults and call them out explicitly.

## Step 1: Architecture (the generic plumbing)

```
[Browser]  ←──── HTTP + WebSocket ────→  [Bun server]  ←─── stdio MCP ───→  [Claude Code session]
   ↑                                          │                                     │
   │                                          │ notifications/claude/channel        │
   │                                          ├─── (push: comment + meta) ─────────→│
   │                                          │                                     │
   │                                          │←─── tool calls (mark_addressed,     │
   │                                          │     update_node, update_data) ──────│
   │                                          ↓
   │                                  [data.json + comments.json on disk]
   │                                          │
   └────── live refresh via WebSocket ────────┘
```

This plumbing is domain-agnostic. The only parts that change per artifact:
1. **`data.json` shape** — whatever structure your viz needs.
2. **The `render` function in `index.html`** — how to paint `DATA` into the DOM.
3. **Which tools the MCP server exposes** — `mark_addressed` is always there; `update_node` / `update_data` are optional.
4. **The MCP server's `instructions` field** — tell Claude how to interpret the specific comments.

## Step 2: Scaffold

Create this layout:

```
<plugin-name>/
├── .claude-plugin/plugin.json
├── .mcp.json
├── package.json
├── server.ts
├── index.html
├── data.json       # your viz state shape
└── comments.json   # { "comments": [] }
```

Start from the bundled templates in `assets/`:
- `assets/plugin.json.template` → `.claude-plugin/plugin.json`
- `assets/mcp.json.template` → `.mcp.json`
- `assets/package.json.template` → `package.json`
- `assets/server.ts.template` → `server.ts`
- `assets/index.html.template` → `index.html` (minimal — has pin overlay, comment panel, WebSocket, no viz)
- `assets/data.json.template` → `data.json`
- `assets/comments.json.template` → `comments.json`

Replace `__PLUGIN_NAME__`, `__PLUGIN_NAME_UPPER__`, `__PORT__`, `__TITLE__`, `__DESCRIPTION__` placeholders. Run `bun install` in the plugin directory.

## Step 3: Build the viz

The template `index.html` is a blank canvas with all the comment plumbing already wired. Implement `window.renderArtifact(DATA)` to paint `DATA` into `#content`. Every element that should be commentable gets `data-node-id="<your-id>"`. Elements without `data-node-id` are still commentable via freeform pins (the script auto-detects the nearest ancestor with an id as the anchor).

### Libraries worth knowing

No runtime dependencies are required — the template is vanilla JS + Bun. Pull in only what you need via ESM CDN imports (`https://cdn.jsdelivr.net/npm/<pkg>@<version>/+esm`). Pick based on the artifact shape:

| Need | Library | Notes |
|---|---|---|
| Any data viz | **D3 v7** | The Swiss Army knife. `d3-sankey`, `d3-scale`, `d3-shape`, `d3-force` etc. are all available. **Gotcha**: d3-sankey 0.12 UMD is broken on d3 v7 — use ESM and spread the frozen namespace. See `references/troubleshooting.md`. |
| Declarative charts | **Chart.js** / **Plotly.js** / **ApexCharts** | Chart.js is lightest; Plotly supports more chart types; ApexCharts is the prettiest out of the box. |
| Grammar-of-graphics | **Observable Plot** | `@observablehq/plot` — built on D3, much less ceremony. Great for quick analytical viz. |
| Network / graph editors | **Cytoscape.js** / **Sigma.js** / **vis-network** | Cytoscape if you need styling power; Sigma for very large graphs; vis-network for quick wins. |
| Canvas / interactive 2D | **Konva.js** / **Fabric.js** / **Pixi.js** | Konva is most ergonomic for "shapes you can drag around". Pixi is best for perf-critical cases. |
| 3D / WebGL | **Three.js** / **regl** | Three.js for scenes; regl for pure shader work. |
| Flow diagrams | **Mermaid.js** / **React Flow** / **@xyflow/react** | Mermaid is zero-config but read-only; React Flow lets users drag nodes. |
| Maps | **Leaflet** / **MapLibre GL** | Leaflet is the simplest; MapLibre is vector + GPU. |
| Tables | **Tabulator** / **AG Grid (community)** | Tabulator for ergonomics; AG Grid for scale. |
| Code editors | **CodeMirror 6** / **Monaco** | CodeMirror ships lighter; Monaco is VS Code's editor verbatim. |
| Markdown | **marked** / **markdown-it** | Both fine; marked is smaller. |
| State | **Nanostores** / **Zustand** | Only if vanilla JS state becomes unmanageable. Most artifacts don't need this. |
| Animation | **Motion One** / **GSAP** | Motion One is tiny and web-native. GSAP for timeline-style animation. |
| Icons | **Lucide** / **Heroicons** / emoji | Inline SVG is fastest; Lucide has a clean aesthetic. |

For styling: plain CSS works. If you want utility-first, use Tailwind via the CDN JIT (`https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4`). Skip it if the artifact is small — the template already has a clean design-system.

## Step 4: Shape `data.json` for your artifact

Whatever your viz needs. Common patterns:

```json
// Funnel/dashboard style
{ "nodes": [{"id": "...", "label": "...", "count": 123 }], "edges": [{"from": "...", "to": "..."}] }

// Graph/network
{ "nodes": [{"id": "n1", "label": "A", "x": 100, "y": 50 }], "links": [{"source": "n1", "target": "n2"}] }

// Kanban
{ "columns": [{"id": "todo", "title": "Todo", "cards": [{"id": "c1", "title": "..."}]}] }

// Timeline
{ "events": [{"id": "e1", "ts": "2026-01-01", "label": "..." }] }
```

No schema is enforced by the server beyond "valid JSON object". The `update_node` tool walks `data.funnel` and `data.sideEvents` by default — rename or generalize that lookup in `server.ts` if your shape differs.

## Step 5: Register in the project's `.mcp.json`

Add to `<project-root>/.mcp.json`:

```json
{
  "mcpServers": {
    "<plugin-name>": {
      "command": "bun",
      "args": ["run", "--cwd", "<absolute path to plugin dir>", "--silent", "start"]
    }
  }
}
```

Use the absolute path. `.mcp.json` is project-scoped — Claude loads it only when launched from the project root.

## Step 6: Hand off to the user

Give the user a copy-pasteable block. Fill in the REAL port and URL you picked — don't leave `__PORT__` placeholders in the message you send. Also list the REAL tools you exposed in server.ts (may just be `mark_addressed`, or include `update_node` / custom tools if you added them).

```
Setup complete. ⚠️ The current session (this one) CANNOT receive channel events — you must spawn a new one.

1. Stop anything on port <PORT>:
     kill $(lsof -ti:<PORT>) 2>/dev/null

2. Launch a NEW Claude Code session with the channel attached:
     claude --dangerously-load-development-channels server:<plugin-name>

   Approve the MCP server prompt the first time it appears.

   Optional: add --dangerously-skip-permissions so the new session auto-approves
   tool calls while it's iterating on the artifact (no "approve?" prompts):
     claude --dangerously-load-development-channels server:<plugin-name> --dangerously-skip-permissions

3. The new session prints to stderr (confirm the URL it actually binds to):
     <plugin-name>: http://localhost:<PORT>

4. Open http://localhost:<PORT> in your browser.

   • Toggle "Pin mode: on" in the top-right — pins ONLY drop while pin mode
     is enabled. Click it again (or press Esc) to turn it off so you can
     interact with the artifact normally.
   • With pin mode on: click anywhere → type → Submit. Each pin push-delivers
     to the new session with position, anchor element, and a context snippet.
     Claude responds via mark_addressed; the pin turns green; the reply
     renders beneath.

To verify wiring, run /mcp in the new session:
  <plugin-name> · ✔ connected — tools: <list-your-actual-tools>

If anything misbehaves, see references/troubleshooting.md.
```

Critical reminders to state plainly in your reply, not just inside the code block:

- **The current session cannot receive channel events.** Channel notifications only flow to the session that loaded the plugin via `--dangerously-load-development-channels`. Spawning a new terminal is not optional.
- **Tell the user the actual URL.** Include the real `http://localhost:<PORT>` (with whatever port you picked) in your reply so they can click it. Don't leave `__PORT__` placeholders.
- **Pin Mode is off by default.** First-time users will click and nothing happens; they'll think it's broken. Mention the top-right toggle explicitly.
- **`--dangerously-skip-permissions` is optional, not default.** Offer it but don't require it — some users want to review every tool call.

## Example walk-throughs

### Walk-through A: "A kanban board I can pin comments on"

1. **Interview** — kanban columns are "Todo / In Progress / Done". Each card has `id`, `title`, `description`. No external data source; user will add cards by hand. No redaction. Plugin name: `kanban`.
2. **Scaffold** — copy templates, name everything `kanban`.
3. **`data.json`** — `{ "columns": [{ "id": "todo", "title": "Todo", "cards": [] }, ...] }`.
4. **`renderArtifact`** — paint three columns, each card rendered as a `<div data-node-id="card_<id>">`. Columns themselves get `data-node-id="col_<id>"`.
5. **Tools** — add `add_card(column_id, title, description)` and `move_card(card_id, to_column_id)` tool handlers alongside `mark_addressed`. Update `server.ts` tool list + CallToolRequestSchema switch.
6. **Instructions field** — tell Claude: comments anchored to a card are feedback on that card; comments on a column are feedback on the column strategy; freeform comments might be general product questions.
7. **Launch instructions** — standard block.

### Walk-through B: "A graph editor for my data model"

1. **Interview** — nodes are tables, edges are foreign keys. Data comes from the user's Prisma schema (read via file system). User wants to pin comments on tables/columns to ask "why is this indexed?" etc.
2. **Scaffold** — plugin name: `schema-explorer`.
3. **Library** — Cytoscape.js (drag/zoom included) or React Flow.
4. **`data.json`** — `{ "tables": [{ "id": "User", "columns": [...], "x": 100, "y": 50 }], "edges": [...] }`. Initial positions via a force layout on first render.
5. **Pre-populate** — before launching, read `prisma/schema.prisma` and bake the graph into `data.json`.
6. **Tools** — `mark_addressed`, `update_node` (to reposition a table), `add_note(node_id, text)` to attach Claude's insight as a sticky note rendered on the table card.
7. **Instructions field** — tell Claude: comments on a table are schema questions; comments on an edge are foreign-key questions; freeform with a context_snippet of "relationship" is about overall data model.

### Walk-through C: "An image annotator where I ask Claude about regions"

1. **Interview** — user drops an image path; wants to click regions and ask Claude questions about them (OCR, object description, etc.).
2. **Scaffold** — plugin name: `image-annotator`.
3. **`data.json`** — `{ "imagePath": "/path/to/image.png", "regions": [] }`.
4. **`renderArtifact`** — render the image; overlay a canvas for clicks; freeform pin coordinates directly encode the region of interest.
5. **Tools** — `mark_addressed` is all you need (regions ARE the comments, since every click is a freeform pin at (x,y)).
6. **Extra** — in Claude's instructions, tell it to crop the region from the image (via the Read tool on the file with offset/region) to answer accurately.

## Common pitfalls (read `references/troubleshooting.md` for full diagnoses)

- **Channel meta must be `Record<string, string>`.** Numbers, nulls, booleans → Zod throws → MCP transport closes silently. Always `String()` everything and drop null/undefined keys via spread.
- **Bun.serve EADDRINUSE.** Wrap in try/catch; on `EADDRINUSE`, log "running stdio-only" and `process.stdin.resume()`. Don't crash — multiple Claude sessions can share state files.
- **Orphan bun on port.** If you ran `bun server.ts` standalone, killing the parent doesn't kill it. `lsof -ti:<port> | xargs kill` to free.
- **CSS variables don't resolve as SVG attribute values.** Use literal hex in `.attr("fill", ...)`, not `var(--green)`.
- **d3-sankey 0.12 UMD breaks on d3 v7.** Use ESM imports, spread the frozen namespace.
- **Edits to `server.ts` don't hot-reload.** After editing, `/mcp` reconnect in the channel session — or kill the bun process and Claude respawns.
- **DELETE comment must NOT call deliverChannel.** Otherwise Claude wastes turns answering removed comments.

## Files in this skill

- `assets/plugin.json.template` — `.claude-plugin/plugin.json`
- `assets/mcp.json.template` — `.mcp.json` (plugin-internal, references `${CLAUDE_PLUGIN_ROOT}`)
- `assets/package.json.template` — `package.json` with the MCP SDK dep
- `assets/server.ts.template` — Bun HTTP + WS + MCP stdio + tools, with EADDRINUSE handling and string-only channel meta
- `assets/index.html.template` — minimal artifact scaffold: pin overlay, comment panel near click, WebSocket, delete-without-notify. Paint your viz into `#content` via `window.renderArtifact(DATA)`.
- `assets/data.json.template` — empty shape placeholder
- `assets/comments.json.template` — `{ "comments": [] }`
- `references/troubleshooting.md` — every gotcha we've hit, with one-liner fixes
- `references/architecture.md` — deeper rationale (why channels > polling, why stdio+HTTP in one process, when to deviate)
