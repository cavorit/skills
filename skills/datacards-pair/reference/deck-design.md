# Laying Out a Deck

A deck where every single card is fine can still be a weak dashboard. These
points are what users had to correct most often. They are independent of the
subject of the project.

## Before the first draft

1. **Find the order in the information.** Almost every subject has one:
   hierarchy (overview, part, single object), time (past, now, forecast) or
   cause and effect (set, effective values, effect, assessment). The order
   groups the cards and gives the reading direction, usually from top left to
   bottom right, ending at the conclusion. A deck without a recognizable
   order looks like a storage shelf.
2. **Find the eyecatcher.** One picture that is understood without reading
   and that belongs to the subject: a map for something spatial, a section or
   schematic for something technical, a process picture for a workflow. Give
   it the best area and work it out properly: real computed values in the
   picture, careful labels, reaction to the controls. A rough sketch is rated
   much worse than a detailed one. Generate it in Python (for example SVG as
   text), not in JavaScript, and draw single-color parts with `currentColor`
   so that light and dark mode both work.
3. **Check the template list** for building blocks and
   [known-limitations.md](known-limitations.md) for their weak spots.

## Cards

- **Build repeated things once.** For several objects of the same kind use
  one selector and one set of cards, not one group of cards per object.
- **The central quantity gets its own control** in a prominent place.
  Presets are an addition, not a replacement.
- **Show cause next to effect.** Put the resulting values next to the
  controls that produce them. Show a chosen value as a number, not only as a
  slider position. A parameter belongs next to the chart it changes.
- **Keep control cards small**, text cards only as large as their content.
  Large half-empty cards look unfinished. Rather one card less.

## Consistency

- **One quantity, one color, on the whole deck.** Closely related quantities
  share a color and differ by line style.
- **Same quantity, same axis.** When several cards show the same quantity or
  the same time span, give them the same axis, value range, margins and card
  height so the information runs from one card into the next. A time control
  belongs directly at the time series, with the same width and scale.
- **Several decks on one subject are a series.** The same thing sits at the
  same place in the same size on every deck.

## Color

- **Color carries meaning.** Red reads as alarm. Use it when something is
  wrong, not to tell two curves apart.
- Use neutral colors for what merely is, and the signal color once a limit
  is crossed. Calm backgrounds with the important part in front.

## Language

- **Write in the language of the readers**, with their terms, units and
  number formats.
- **No identifiers from the code** on a deck: no variable names, dictionary
  keys or column names. Selectors get readable entries that map to internal
  keys.
- **Every number has a unit**, and a card title says what the number means
  without explanation.
