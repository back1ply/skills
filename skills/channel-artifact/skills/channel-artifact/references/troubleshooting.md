# Channel artifact — troubleshooting

Every failure mode we've hit while building this pattern, with the one-liner fix.

## Contents

- Setup / launch
- UI rendering
- Comments / pins
- Multi-instance / state-sharing
- Useful diagnostics
- Known-good launch command

## Setup / launch

### `/mcp` shows `customer-journey · ✘ failed`

Three common causes, in order:

1. **Port already in use.** Another bun process owns the port. Check with `lsof -ti:<port>` → `kill <pid>`. Then `/mcp` reconnect.
2. **Project `.mcp.json` wasn't loaded.** The server registration is project-scoped — Claude must have been launched from the project root directory. Verify with `pwd` before `claude --dangerously-load-development-channels server:<name>`.
3. **First-time approval prompt dismissed.** Project MCPs require user approval on first run. If you hit Escape or the prompt never appeared, the server stays disabled. `/mcp` → select the server → "enable".

### `Connection closed` or `MCP error -32000` right after launch

The server process crashed. Likely causes:

- **Channel meta contains non-strings.** Numbers, nulls, booleans in the `meta` object cause Zod validation to throw in Claude's channel handler. The MCP transport closes silently after the first notification. Always `String(value)` every meta field and drop keys where value is null/undefined via spread:
  ```ts
  ...(comment.anchorNodeId ? { anchor_node_id: comment.anchorNodeId } : {}),
  ```
- **`Bun.serve` threw uncaught.** If `EADDRINUSE` isn't caught, the process exits. Wrap `Bun.serve` in try/catch; on `EADDRINUSE`, log a warning and `process.stdin.resume()` so stdio MCP stays alive.

### Pin a comment but nothing happens in Claude

The UI saved the comment but the channel notification didn't reach any session. Diagnose:

1. Check `lsof -ti:<port> | xargs ps -p` — what's the PPID?
   - **PPID = 1**: orphan bun. Started standalone (`bun server.ts`) or survived its parent. No Claude is listening on its stdio. `kill <pid>` and relaunch with `claude --dangerously-load-development-channels server:<name>`.
   - **PPID = Claude's PID**: Claude spawned it, stdio is connected. Should work. Check `/mcp` for connection status and tool list.
2. If `/mcp` shows the server healthy but pins still don't trigger, look at the channel session's terminal output — a `<channel source="<name>">` event should print when a comment arrives. If not, the notification is being sent but not delivered (rare; usually the meta-types bug).
3. If you recently edited `server.ts`: **edits don't hot-reload**. `/mcp` reconnect to respawn.

### Orphan bun stays after Claude exits

Claude's spawned bun can outlive the session if the MCP SDK doesn't cleanly close stdin. Always clean up before relaunching:
```bash
kill $(lsof -ti:<port>) 2>/dev/null
```
If Bun.serve dies (port taken) but stdio is kept alive via `process.stdin.resume()`, the process can hang indefinitely. That's intentional for shared-state scenarios, but confusing when the first owner exits — the backup takes over silently.

## UI rendering

### Sankey is blank, no errors

d3-sankey `0.12.x` UMD expects `d3.array` and `d3.shape` namespaces (d3 v4 layout). d3 v7 is flat — those namespaces don't exist, so `d3.sankey` is undefined and `renderSankey()` throws inside `render()`, silently stopping everything afterward.

Fix: use ESM imports, spread the frozen namespace before adding extras:

```html
<script type="module">
  import * as d3mod from "https://cdn.jsdelivr.net/npm/d3@7/+esm";
  import { sankey, sankeyLinkHorizontal } from "https://cdn.jsdelivr.net/npm/d3-sankey@0.12.3/+esm";
  window.d3 = { ...d3mod, sankey, sankeyLinkHorizontal };
  window.dispatchEvent(new Event("d3-ready"));
</script>
```

Then boot your main script on the `d3-ready` event (ESM modules load after the non-module body script runs, so you need to wait for it).

### `Cannot assign to property 'sankey' of [object Module]`

ESM module namespaces are frozen. Can't do `d3.sankey = sankey`. Spread into a plain object first:
```ts
window.d3 = { ...d3mod, sankey, sankeyLinkHorizontal };
```

### `Error: missing: 0` inside d3-sankey

`.nodeId(d => d.id)` tells sankey to look up nodes by string `id`, but links use numeric indices. Switch links to string ids:
```ts
// BROKEN:
{ source: 0, target: 1, value: 100 }
// WORKING:
{ source: "landing", target: "pricing", value: 100 }
```

### Sankey rects render with no fill (invisible)

CSS variables (`var(--green)`) don't resolve as SVG attribute values — only as CSS `style` rules. Use literal hex in `.attr("fill", ...)`:
```ts
// BROKEN:
.attr("fill", "var(--green)")
// WORKING:
.attr("fill", "#16a34a")
```

### Whole page below header is blank

Usually a chain reaction: `renderSankey()` throws, and the rest of `render()` (KPIs, funnel, side events) never runs. Check DevTools console for the first error. Common culprits are the three d3-sankey issues above.

## Comments / pins

### Delete returns 404

The running bun is stale — `server.ts` was edited but the server wasn't respawned. `/mcp` reconnect, OR if an orphan is holding the port, `kill $(lsof -ti:<port>)` and reconnect.

### Claude responds to comments I deleted

`deliverChannel` was called on the DELETE path. It must NOT be — only adds should notify Claude. Remove the call from the `DELETE /comment/:id` branch.

### Pin drops but panel opens in the wrong place

The panel uses `position: absolute` with `left/top` computed from click coords and clamped to viewport. If it's far off, check:

- The parent has `position: relative`/`static` on `body` (it should — `body` is the offset parent for `position: absolute` at the document level).
- The click event is `e.pageX`/`e.pageY`, not `e.clientX`/`e.clientY` (pageX/Y include scroll).
- `positionPanelNear` clamps against `window.scrollY + window.innerHeight` — verify the math if you customized it.

### Comment panel bottom-right instead of near click

You still have `position: fixed; right: 24px; bottom: 24px;` from a draft version. Change to `position: absolute; z-index: 70;` and call `positionPanelNear(x, y)` from every `openPanel*` function.

### Floating pin marker is hard to click

Default size (16px) is too small. Bump to 22px with a 2px white border, and keep the delete × visible whenever the pin is `active`:
```css
.floating-pin .delete-btn { width: 22px; height: 22px; ... }
.floating-pin:hover .delete-btn,
.floating-pin.active .delete-btn { opacity: 1; }
```

## Multi-instance / state-sharing

### Two Claude sessions want the same channel — one fails

Expected. The first session to spawn bun owns the HTTP port; the second hits `EADDRINUSE`, logs `running stdio-only`, and serves tool calls against the shared `data.json` + `comments.json`. Both sessions can mark comments addressed, update nodes, etc. Only the first session's bun emits WebSocket broadcasts — the browser connected to port 5180 only sees updates from that one. This is fine for most workflows.

### WebSocket keeps disconnecting

The server was restarted (`/mcp` reconnect or process died). The client reconnects on close with a 2s backoff — see the `connectWs()` pattern in the template. If reconnects fail continuously, the server is actually down — check `lsof -ti:<port>`.

## Useful diagnostics

```bash
# Is anything on the port?
lsof -ti:<port>

# Who owns it?
lsof -ti:<port> | xargs ps -p

# PPID = 1 → orphan. PPID = claude PID → healthy spawn.

# Check MCP process tree
pgrep -fl "bun server.ts"

# Tail server stderr (captured by Claude)
# In the channel session, look for the line:
#   <plugin-name>: http://localhost:<port>
# If you see "running stdio-only" instead, another instance owns the port.

# Force a clean reset
kill $(lsof -ti:<port>) 2>/dev/null
# Then in Claude: /mcp → reconnect
```

## Known-good launch command

From the project root (the directory with `.mcp.json`):
```bash
claude --dangerously-load-development-channels server:<plugin-name>
```

If this is the first time, approve the MCP server prompt. The new session prints `<plugin-name>: http://localhost:<port>` to stderr when the server boots. Open that URL.

To verify: `/mcp` should show `<plugin-name> · ✔ connected` with tools `mark_addressed`, `update_node`, `update_data`.
