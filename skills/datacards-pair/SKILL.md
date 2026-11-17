---
name: datacards-pair
description: >-
  Drive a live DataCards project as a workspace: run Python in the same marimo
  kernel the user does, inspect live notebook state, commit durable notebook
  changes, and place cards on decks. Use when the user wants to pair on a
  DataCards project (usually running in the cloud) or on an active marimo
  session.
allowed-tools: Bash(bash **/scripts/discover-servers.sh *), Bash(bash **/scripts/execute-code.sh *), Read
---

## DataCards

DataCards is a platform that orchestrates multiple marimo notebooks into a
graph of notebooks. A project is a workspace of notebooks served by one marimo
server behind the DataCards server. Notebooks exchange data through the data
catalog: `dc.data.publish("namespace.key", value)` in one notebook,
`dc.data.consume("namespace.key")` in another.
Every publish/consume pair is an edge of the project's process graph, which
the DataCards canvas draws as notebook nodes and variable nodes.

Notebooks place cell outputs as *cards*: each cell appears as a card in
the notebook's Exposé view, and cards can be placed on *decks*, grid-based
visual dashboards (`columns` x `rows` units) that sit next to the graph on the
canvas. A deck card shows the live output of its cell, so a deck composes a
dashboard from cells of several notebooks. Decks, cards and the card-store
templates are owned by the DataCards server, not by any notebook file.

In DataCards notebooks `import datacards as dc` is the convention. The
`datacards` package re-exports the marimo API, so `dc.ui`, `dc.md` and
`dc.data` are marimo's; `import marimo as mo` works the same way.
You must use `dc` instead of `mo` in notebook cell code.

### Product rules

These rules describe how DataCards is meant to be used. Work that breaks them
gets rejected even when it runs. They take precedence over the marimo guidance
further down and in the reference files. The reasons are in
[product.md](reference/product.md).

1. **Build with DataCards, not inside it.** Controls come from the card store
   (`ctx.list_templates()`) or `dc.ui.*` and sit on the deck as separate
   cards. Never build one card that brings its own controls, state and logic
   (a large anywidget or HTML/JavaScript block).
2. **Logic is visible.** Computation and business logic live in notebook
   cells. Data that crosses notebooks goes through `dc.data.publish` /
   `dc.data.consume`, so the graph shows it.
3. **Stay in the design system.** Look at the template list first and use the
   existing building blocks. Build something custom only where no block
   exists, and never give it its own color scheme: light and dark mode must
   both work.
4. **Ask before you trade a rule away.** When a requirement seems to need
   something outside these rules (smooth animation, a missing component),
   put the trade-off to the user before building. Do not decide alone and
   mention it afterwards.
5. **A notebook is a document.** Each notebook starts with a markdown cell
   stating purpose, input and output. Domain logic, formulas and data sources
   are explained in markdown; code comments are for coding detail only.
6. **Publish only what another notebook needs.** Use `dc.data.publish` only
   when a second notebook really consumes the value; inside a notebook use
   the local variable. Use `dc.data.publish/consume` only in notebook cell
   code, never in the scratchpad.
7. **The workspace is a git repository.** DataCards commits and pushes it
   automatically. Never store large files or files that change often in it
   unprotected: use a temporary directory outside the workspace, or a folder
   listed in `.gitignore`. This holds especially for SQLite databases and
   their `-wal`/`-shm` files. Treat all such files as ephemeral: on a cold
   start, the first execution of every kernel must recreate them without
   user interaction.
8. **Lasting storage that does not fit git goes to object storage.** Ask the
   user to provision an S3 bucket and hand over the credentials, or to put
   them in a `.env` file in the workspace (listed in `.gitignore`). Use it
   from notebook code with `from obstore.store import S3Store`. See
   [product.md](reference/product.md#files-and-storage).

### Work loop

1. **Connect** and run the required first kernel command (below).
2. **Survey the project before changing it.** List the notebooks (the
   sessions on the project URL), read their cells (`ctx.cells`), list the
   decks and their cards (`await ctx.list_decks()`), and look at the graph
   (`await ctx.screenshot_graph()`). Reuse what exists and leave nothing
   orphaned. If the project contains a briefing, plan or design notes, read
   them.
3. **Check feasibility from the kernel.** Test network access and fetch every
   data source once from the kernel, not from your own environment: the two
   can reach different hosts. Look at the shape and value range of the data
   before setting thresholds and scales.
4. **Plan, and ask where rule 4 applies.**
5. **Build.** Read [decks.md](reference/decks.md) before placing cards and
   [deck-design.md](reference/deck-design.md) before laying out a deck.
6. **Verify** with the checklist below.
7. **Hand over.** Say what you built, what you could not verify, and anything
   you left behind (files, packages, an agent-caused error state).
   If the `dc-feedback` skill is installed, offer to send lessons learned
   from the session with it.

### Verification checklist

A green graph only means that no cell raised an exception.

- **Run the cell itself.** A test in the scratchpad proves nothing about the
  cell: the scratchpad shares already-imported modules with the kernel. Give
  each cell the imports it needs, run it with `ctx.run_cell(...)` and check
  `ctx.cells[...].status` and `.errors`.
- **Check the values.** Compare formulas, thresholds, units and start values
  with the briefing. A number that is always 0 or always 100 %, a point stuck
  at the edge of a chart or an empty plot is a computation error, not a
  layout problem.
- **Look at the finished deck** with `await ctx.screenshot_deck(deck_id)`:
  cut-off charts, double titles, overflowing controls and overlapping labels
  only show there. Check that every card shows the cell you meant.
- **Operate every control once** and see which number changes. A control
  without a visible effect does not belong on the deck. With a selector, look
  at every option.
- **Name what you did not verify** in the handover (interaction in the
  browser, light mode, a selection you never looked at).

### Connecting to a DataCards project

The primary use case is a project running in the DataCards cloud. Its URL has
the form `https://<host>/<team>/<project>/`; the project's "Pair with agent"
dialog shows that URL together with a project token (`dc_sk_proj_...`). Pass
the URL as `--url` and the token via `MARIMO_TOKEN` (preferred) or `--token`.
All notebooks of a project are sessions on that one URL. With more than one
notebook open, run the command once without a selector: it fails with the
list of sessions (`<session id>  <path>`). Then pass `--file` with a path
exactly as listed (a shortened name does not match), or `--session` with the
id:

```bash
MARIMO_TOKEN=dc_sk_proj_... bash /absolute/path/to/datacards-pair/scripts/execute-code.sh \
  --url https://<host>/<team>/<project>/ --file <path as listed> \
  -c "import marimo._code_mode as cm; help(cm)"
```

Everything below about marimo (the kernel, the scratchpad, `cm`, the graph
contract) applies unchanged to each notebook of the project.

### DataCards functions in code mode

Besides the marimo cell API, the code-mode context (`ctx = cm.get_context()`)
exposes the DataCards actions a human has in the frontend. They are methods of
`ctx`, not of the `cm` module:

- **Card title and size** - `ctx.create_cell(...)` and `ctx.edit_cell(...)`
  take `title=` and `size=(width, height)` in grid units.
- **Decks and cards** - `ctx.list_decks()`, `ctx.get_deck(...)`,
  `ctx.add_card_to_deck(...)`, `ctx.edit_card_on_deck(...)`,
  `ctx.remove_card_from_deck(...)`.
- **Templates** - `ctx.list_templates()`, `ctx.add_template_to_deck(...)`,
  `ctx.assign_template_to_notebook(...)`.
- **Screenshots** - `ctx.screenshot(cell)`, `ctx.screenshot_deck(deck_id)`,
  `ctx.screenshot_graph()`, `ctx.close_screenshot_session()`.

Usage, rules and how building blocks behave on a deck are in
[decks.md](reference/decks.md).

### Which reference to read when

| When | Read |
|------|------|
| You want to know why a product rule exists, or how projects, notebooks and the sandbox work | [product.md](reference/product.md) |
| Before placing cards, using templates or taking screenshots | [decks.md](reference/decks.md) |
| Before laying out a deck | [deck-design.md](reference/deck-design.md) |
| Before the first draft of a deck | [known-limitations.md](reference/known-limitations.md) |
| Something hangs, times out or turns red | [troubleshooting.md](reference/troubleshooting.md) |
| The script cannot reach or select a session | [execution-context.md](reference/execution-context.md) |


## marimo Notebooks

marimo is a reactive Python runtime for building reproducible Python programs
(marimo notebooks). Cells are connected by the variables they define and
reference. Running a cell re-executes dependents in dataflow order. The active
runtime holds the kernel namespace, cell state, and dataflow graph. The
notebook (`.py` file) is the artifact the kernel writes from that state while a
session is running.

A user interacts with the same runtime via a notebook UI with cells, outputs,
and widgets.

**WARNING. The active runtime is the source of truth.** During a session, you
SHOULD NOT modify the associated `.py` file directly. File edits WILL NOT reach
the active kernel or user, and the kernel may overwrite them on save. Use
`marimo._code_mode` (`cm`) for notebook changes. Reading disk is fine, but
prefer `ctx.cells[...].code` for current cell code.

The harness reports the absolute path to this `SKILL.md`. Resolve bundled
`scripts/...` and `reference/...` paths from its parent directory, even when
the current working directory is a notebook workspace. In command examples,
replace `/absolute/path/to/datacards-pair` with that directory.

## Required first kernel command

Start every code-mode session with this dedicated command:

```bash
bash /absolute/path/to/datacards-pair/scripts/execute-code.sh \
  --url http://localhost:2718 \
  -c "import marimo._code_mode as cm; help(cm)"
```

Follow this order for each kernel, including read-only tasks:

1. Run the inspection command once.
2. Wait for successful `help(cm)` output.
3. Then use `cm.get_context()` or another `cm` API in a later call.

Do not run task-specific `cm` code before the inspection command succeeds.

## Connect to a Notebook

Use the bundled `execute-code.sh` from the reported skill directory or MCP
(`execute_code(...)`) to run Python in a live marimo kernel.

`execute-code.sh` always takes `--url`. If the user provides a notebook URL,
run the required inspection against it directly:

```bash
bash /absolute/path/to/datacards-pair/scripts/execute-code.sh \
  --url http://localhost:2718 \
  -c "import marimo._code_mode as cm; help(cm)"
```

After that command succeeds, pass task code with `-c CODE`, `-` for stdin, or
a file path:

```bash
bash /absolute/path/to/datacards-pair/scripts/execute-code.sh \
  --url http://localhost:2718 - <<'PY'
import marimo._code_mode as cm

async with cm.get_context() as ctx:
    cid = ctx.create_cell("x = df.head()")
    ctx.run_cell(cid)
PY
```

If the user gives no URL, find or start a notebook. Look for a running server
with `bash /absolute/path/to/datacards-pair/scripts/discover-servers.sh`, MCP
`list_sessions()`, or local process context, and pass the `url` it reports to
`--url`. With one notebook open, the script targets it automatically; with
several, pass `--file` with the notebook's file key.

If no server is running and the user wants a notebook, start marimo with
`--no-token` (and without `--headless`) so it auto-registers for discovery. The
notebook UI must be open for `execute-code` to target it. The right invocation
depends on context (project tooling, global install, sandbox mode). If the
notebook file contains a PEP 723 `#
/// script` header, it MUST be opened with `--sandbox` — otherwise marimo
ignores the inline dependencies. See
[finding-marimo.md](reference/finding-marimo.md) for the full decision tree and
[execution-context.md](reference/execution-context.md) for selector resolution,
scripts, MCP, and shell quoting.

## Scratchpad Scope

`execute-code` evaluates Python in marimo's scratchpad: a temporary namespace
with a shallow copy of the kernel globals. Notebook variables are available by
name, but new top-level bindings and rebindings are discarded after each call.
In-place mutations to notebook-owned objects can persist because those names
still reference live objects.

Each call reports stdout and stderr from the scratchpad, plus console output
from notebook cells it causes to run, including reactive descendants.

### Ordinary Python

Use ordinary Python in the scratchpad to inspect variables, sample data, test
transformations, probe APIs, check imports, and read widget state.

```python
print(df.head())

x = 10
print(x)
```

Here `df` comes from notebook globals, while `x` is a scratchpad-local binding.
`x` exists for this call only and WILL NOT be added to notebook globals.

### Persist with `cm`

Top-level scratchpad assignments and rebindings are temporary. To persist work,
including new variables, you MUST submit changes through `marimo._code_mode`
(`cm`).

`marimo._code_mode` is a PRIVATE, UNSTABLE agent API (note the leading
underscore). It exists for tools like this skill to drive a live kernel from
the scratchpad. DO NOT import it from notebook cells, library code, or
anything a user would run — methods can change or disappear across marimo
versions and kernels. Treat every `import marimo._code_mode as cm` as
scratchpad-only.

Open a code-mode context to queue notebook changes.

```python
import marimo._code_mode as cm

async with cm.get_context() as ctx:
    cid = ctx.create_cell("x = df.head()")
    ctx.run_cell(cid)
```

The scratchpad supports top-level async code. Use `async with` directly;
wrapping it in `asyncio.run(...)` is unnecessary and can conflict with the
kernel's event loop.

After this block exits and the new cell runs, `x` is notebook state. Later
scratchpad calls can read `x` by name. Code later in the same scratchpad call
should read `ctx.globals["x"]`, because the scratchpad namespace was copied
before the cell ran.

Inside the context, queued mutation methods are synchronous. Call them
directly; do not `await` them. Each call queues an operation for marimo to
apply when the context exits normally. If the block raises, the queue is
discarded.

On clean exit, marimo applies packages, validates and applies structural cell
changes, runs queued cells, then may run dependents. Validation is only
structural since queued cell runs can still error. `create_cell` and
`edit_cell` change notebook structure only. Use `run_cell` to execute. 

`create_cell` currently defaults to `hide_code=True`, which collapses the code
editor in the UI. Pass `hide_code=False` if the user wants created cells to
be visible without manually expanding them.


## Marimo Rules

marimo imposes a small contract on notebook code so it can keep the notebook as
a directed acyclic graph (DAG):

- **No cycles** - cells cannot depend on each other in a cycle.
- **No public redefinitions across cells** - each name has one owning cell.
- **No wildcard imports** - `import *` prevents static analysis of definitions.

These rules keep the kernel, UI, and saved artifact consistent.

When `cm` submits a cell body, marimo parses its top-level definitions and
references. A top-level name enters the graph unless it is private with a
leading underscore.

```python
# Public definitions: values, total, i, value, mean
values = np.array([1, 2, 3])
total = 0
for i, value in enumerate(values):
    total += value
mean = total / len(values)
mean
```

```python
# Public definition: mean
_values = np.array([1, 2, 3])
_total = 0
for _i, _value in enumerate(_values):
    _total += _value
mean = _total / len(_values)
mean
```

Use private names for intermediates that no other cell should read. Public
names define the notebook-level dataflow. If a `cm` edit violates the contract,
marimo rejects the structural change and returns the validation error.

## The Notebook's Shape

A notebook is an ordered collection of cells. `ctx.cells` is the document view
and `ctx.graph` is the dataflow view.

```python
for cell in ctx.cells:
    cell  # .id, .code, .name, .config, .status, .errors

ctx.cells["setup"]         # by name
ctx.cells[0]               # by position
list(ctx.cells.keys())     # all IDs, in notebook order
```

Cell IDs are opaque strings which can be queried from the notebook or captured
from `cm` return values:

```python
cid = ctx.create_cell("df = pd.read_csv('data.csv')")
print(cid)   # e.g. 'Hbol'
```

Alternatively, cells can be assigned and referenced by `name`. The graph can be
used to understand its role in the dataflow.

```python
for cid, impl in ctx.graph.cells.items():
    impl  # .defs, .refs   (sets of public names)

ctx.graph.descendants(cid)   # cells that re-run when this one changes
ctx.graph.ancestors(cid)     # cells this one depends on
```

In marimo, deletes are *destructive* so it can be useful to query the
descendants prior to deleting to understand it's impact.

## Writing Notebook Changes

The graph contract keeps marimo able to run and save the notebook. Passing
those checks alone does not guarantee a useful artifact. Committed cells should
still be readable, rerunnable, and editable.

Make durable edits that reuse the notebook's existing names, imports,
dependencies, and UI model. Don't be lazy. Avoid one-off workarounds that pass
`cm` validation but leave a brittle notebook.

### Cell Bodies

Submit the code that belongs in the cell.

- **Submit cell contents** - `create_cell` and `edit_cell` take cell contents,
  not saved-file `@app.cell` wrappers.
- **Read before replacing** - for now, another editor may change a cell between
  scratchpad calls. Before `edit_cell`, read the current body from
  `ctx.cells[...]` and submit the full replacement.
- **Reuse notebook imports** - if `np` already exists, use it or edit the owning
  import cell. DO NOT add `import numpy as _np` just to bypass the graph.
- **Define public names intentionally** - use public names for values later
  cells should reference. Use private `_name` bindings or function locals for
  same-cell intermediates.
- **Define each public name once** - a public name has one owning cell.
  Reassigning it in another cell fails with `Multiply-defined names`; edit the
  owning cell or give the result a new name. See
  [gotchas.md](reference/gotchas.md).
- **Run cells deliberately** - `create_cell` and `edit_cell` change structure
  only. Queue `ctx.run_cell(...)` when the cell should execute.

### Prefer `cm`-Managed Changes

Use `cm` APIs when they exist. Avoid direct file edits, shell package commands,
and scratchpad-only state for changes that should persist.

- **Do not edit the `.py` artifact** - DO NOT use `Edit`, `Write`, or
  `NotebookEdit` on the notebook file during a live session. Use
  `ctx.edit_cell(...)` even for small changes.
- **Manage packages through `cm`** - use `ctx.packages.add()` or
  `ctx.packages.remove()` instead of direct `uv` or `pip`; confirm
  non-obvious dependency changes.
- **Avoid transient paths** - persisted cells should not depend on `/tmp/...`
  unless the work is intentionally transient.
- **Delete deliberately** - deleting a cell removes globals it defines. Reuse
  empty cells when convenient and delete cells left empty after edits.

### UI and Widgets

Inspect the object before changing it. Different UI objects update through
different paths.

- **Set `mo.ui.*` through `cm`** - use `ctx.set_ui_value(element, value)` inside
  `cm.get_context()`.
- **Set anywidget traitlets directly** - synced traitlets are Python
  attributes, for example `widget.value = 5`.

For designing custom visual or interactive output, see
[rich-representations.md](reference/rich-representations.md).

## DataCards Decks, Cards and Screenshots

The deck, card, template and screenshot API is described in
[decks.md](reference/decks.md). Read it before placing cards.

## References

DataCards:

- [product.md](reference/product.md) — how DataCards is meant to be used, the reasons behind the product rules
- [decks.md](reference/decks.md) — deck, card, template and screenshot API, behavior of building blocks on a deck
- [deck-design.md](reference/deck-design.md) — laying out a deck that reads well
- [troubleshooting.md](reference/troubleshooting.md) — the sandbox, reading errors, cleaning up
- [known-limitations.md](reference/known-limitations.md) — temporary workarounds for platform weaknesses

marimo:

- [execution-context.md](reference/execution-context.md) — scripts, MCP, auth, startup, and shell quoting
- [finding-marimo.md](reference/finding-marimo.md) — choosing the right marimo invocation
- [gotchas.md](reference/gotchas.md) — name redefinition, cached module proxies, and notebook traps
- [rich-representations.md](reference/rich-representations.md) — custom widgets and visualizations
- [notebook-improvements.md](reference/notebook-improvements.md) — improving existing notebooks
