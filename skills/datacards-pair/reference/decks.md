# Decks, Cards, Templates and Screenshots

Read this before placing cards on a deck.

## API

In DataCards a notebook's cells appear as *cards*: on the Exposé view of the
notebook and on *decks* (fixed grids of `columns` x `rows` units on the
canvas). The code-mode context `ctx` exposes the same actions a human has in
the frontend. The deck, template and screenshot methods are `async`, apply
immediately on the DataCards server, and work inside or outside `cm.get_context()` (they are not
queued like cell edits):

```python
import marimo._code_mode as cm

ctx = cm.get_context()
async with ctx:
    # Card title and footprint (grid units, 1..24 x 1..12); the size is
    # the card's size in Exposé and its default size on a deck.
    ctx.edit_cell("chart", title="Revenue", size=(4, 2))

decks = await ctx.list_decks()  # Deck(id, columns, rows, cards, ...)
deck = await ctx.get_deck("overview")

# Place a cell of this notebook; position=None takes the first free spot.
card = await ctx.add_card_to_deck("overview", "chart", position=(0, 0))
await ctx.edit_card_on_deck("overview", card, position=(4, 0), size=(2, 2))
await ctx.remove_card_from_deck("overview", card)

# Card-store templates: place one, then assign it to a notebook, which
# inserts and runs the template's cells there (like the "assign" button).
templates = await ctx.list_templates()  # TemplateInfo(id, title, size)
tpl = await ctx.add_template_to_deck("overview", "integer-slider")
result = await ctx.assign_template_to_notebook("overview", tpl, "nb.py")
# or: await ctx.assign_template_to_notebook("overview", tpl, new_notebook="controls")

# Screenshots (headless Chromium; needs `playwright` + chromium):
png = await ctx.screenshot("chart")  # one cell's output
png = await ctx.screenshot_deck("overview")  # the deck on its own page
png = await ctx.screenshot_graph()  # the process graph on the canvas
await ctx.close_screenshot_session()  # when used outside `async with`
```

- **Cards reference cells by notebook path and `dc_id`** - a cell card id is
  `"<notebook path>.py-<dc_id>"`, where the path is relative to the
  workspace root (`"sub/nb.py-<dc_id>"` for a notebook in a folder). The
  `dc_id` is a stable identifier every cell carries (`cell.config.dc_id`);
  it is not marimo's cell id and does not change when the project restarts.
  Pass the cell (id, name, index) and `ctx` derives the card id from the
  current notebook. Pass the same relative path as `notebook_file`
  to `assign_template_to_notebook`. Template cards are `"template:<uuid>"`.
- **Decks are bounded** - a card must fit in `columns` x `rows` and an
  explicit `position=` must not overlap another card; `cm` raises
  `ValueError` (naming the blocking card) when it does not fit and
  `DeckError` when the deck has no free spot left. `add_card_to_deck`
  refuses a cell that is already on the deck; use `edit_card_on_deck` to move
  or resize it.
- **Run before you place** - a deck card shows the cell's output; an unrun
  cell shows nothing. `screenshot_deck` reloads the deck page, waits for
  every card's cell state (a few seconds at most) and captures the deck as it
  is, so a card of a notebook that is not running comes out empty.
- **Check the result** - use `screenshot_deck` / `screenshot_graph` to verify
  a layout the way the user will see it. Screenshots return PNG bytes;
  `as_data_url=True` returns a data URL and `save_to=` also writes the file,
  on the machine running the kernel (in the cloud, inside the project
  sandbox). The DataCards cloud images ship `playwright` and Chromium; a
  local kernel needs `ctx.packages.add("playwright")` and
  `python -m playwright install chromium`.
- **Errors** - `DeckError` for an unknown deck, card or template, a server
  error (the message carries the server's text) or a call outside code mode;
  `ValueError` for a bad position or size; `ScreenshotError` for a missing
  browser or a page that did not render. Use `help(ctx.add_card_to_deck)`
  and friends for the full argument lists.

## How things behave on a deck

- **The card carries the title.** Set the title with `title=` on the cell. Do
  not also give the figure or the control its own title or label that repeats
  it, or the deck shows two titles.
- **One output per deck cell.** A cell that goes on a deck builds exactly one
  output as its last expression. Check tables and intermediate views get
  their own cell.
- **Input cards and output cards look different.** Anything wrapped in
  `dc.ui.*` is a control and renders as an input card. To show a chart as an
  output card, return the figure itself, not `dc.ui.plotly(fig)` or another
  `dc.ui` wrapper.
- **Give charts a fixed height that fits the card.** A chart without a fixed
  height gets cut off. Keep texts on cards short; long labels are truncated.
- **`dc.image(fill_card=True)` crops** to fill the card. For a drawing that
  must stay complete, pass `style={"object-fit": "contain"}`.
- **Use the template's own size.** `ctx.list_templates()` returns each
  template's default size. Start from it instead of guessing a larger one.
- **Moving several cards.** `edit_card_on_deck` checks overlap against the
  current state of the deck, so free the target spot first when you
  rearrange.

## Finding deck cells again

A deck card stays attached to its cell across restarts through the cell's
`dc_id`, so a deck does not have to be laid out again after a restart. Give
cells that go on a deck a name (`name=` on `create_cell` / `edit_cell`) or
at least a title, so you and the user recognize them.

## Getting a screenshot back

Screenshots are taken inside the project sandbox. Do not print the full-size
PNG bytes or data URL: marimo truncates large console output and the image
arrives broken. Either downscale in the kernel first (for example to JPEG
with Pillow) and print that as base64, or write the file with `save_to=` and
fetch it in parts.
