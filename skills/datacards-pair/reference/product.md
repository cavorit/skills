# How DataCards Is Meant to Be Used

The product rules in `SKILL.md` are short on purpose. This file gives the
reasons and the surrounding product knowledge.

## What DataCards is for

DataCards makes a computation transparent. The graph shows which notebook
produces which data and who consumes it. A notebook shows how a result is
computed and documents why. A deck shows results and controls to people who
do not read code. Someone who asks "where is the business logic?" must be
able to find it in the graph and the notebooks.

## Why no app inside a card

A single card with a self-written JavaScript widget that brings its own
slider, buttons, state and theme is "software inside the software":

- The logic is hidden in a JavaScript block. Neither the graph nor the
  notebook cells show it.
- The controls look and behave differently from DataCards controls. Users
  may not even recognize them as controls.
- A built-in color scheme does not follow light and dark mode.
- It bypasses the design system the product is built around.

Use card-store templates and `dc.ui.*` as separate cards instead. Custom
JavaScript is the exception: minimal, only where nothing else works, and only
after the user agreed.

## Slow computations

DataCards does not have to be instant. A computation that takes many seconds
is fine as long as the user sees that something is running and the result is
smooth afterwards. When something is too slow, do not move it into a custom
frontend:

- Compute once and cache (a file in the project folder, `dc.persistent_cache`).
- Pre-render what would otherwise be animated live.
- Show progress while it runs.

## Do not rebuild what the platform shows

- **Status and freshness**: the graph colors notebook nodes by state. Do not
  build your own status display for "is the data current".
- **Provenance**: data sources and citations belong in the notebook's
  markdown. A deck is not a paper; keep source lists off the cards.

## Notebooks

- **Document, not code dump.** Markdown carries the domain content: purpose,
  input, output, model, formulas, business logic. In a notebook that only
  prepares data, the pipeline is the domain content and is explained in
  markdown too. As a rule of thumb, about a third of what a reader sees when
  opening the notebook should be markdown.
- **Each notebook is its own kernel process** and uses memory before it
  computes anything. Split a project into notebooks where the graph gains
  meaning from it, not for every small step, and keep an eye on the
  sandbox's memory when a project grows to many notebooks.
- **Controls next to their consumers.** Put a control into the notebook that
  uses its value unless a second notebook needs it. Every extra hop through
  the data catalog is one more thing that can stall the deck.

## Data flow across notebooks

- A value reaches another notebook only through `dc.data.publish` and
  `dc.data.consume`.
- `ctx.set_ui_value(...)` changes the value in its own notebook. It does not
  run the chain across notebook borders. After changing something upstream
  as an agent, re-run the consuming cells in every downstream notebook, in
  graph order, or later stages keep computing with old values.
- You cannot press "play" on the graph. Say in the handover that the
  end-to-end run and the reaction of the decks to a control in the browser
  are unverified, and ask the user to try them.

## The project folder

The project is a git workspace that the platform saves automatically.
Everything in the project folder ends up in that history.

- Put caches, downloaded data and database files in a folder that is listed
  in `.gitignore`. Create the `.gitignore` before writing the first file.
- Prefer the packages the image already has. Tell the user in the handover
  which packages you added with `ctx.packages.add()`.
