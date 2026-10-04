# Level 2: HTML page with one diagram

One link carries the difficulty, and one diagram of up to ~9 nodes shows it. The page gives the answer on top, the diagram holds the explanation, and the text under it is short.

## Build

1. Pick a `<slug>`: the topic in lowercase Latin letters, words joined by hyphens (`save.md` section 1). Example: "How a cache works" becomes `how-a-cache-works`.
2. Copy the template to a temporary file: `cp <skill-dir>/assets/page.html /tmp/<slug>.html`. `save.md` puts the finished file in place.
3. Fill `<title>` and `<h1>` with the topic.
4. Put the answer in the `.answer` block, in 2-4 sentences. The conclusion must be visible without scrolling.
5. Keep one `<figure>`. Delete the step player, the path switch, the slider, their buttons and the demo script `window.onSlider`. Remove the `stepper` class from the remaining figure.
6. Draw the diagram in `<svg>` by the rules below.
7. In `<figcaption>` write 1-3 sentences: which question the diagram answers.
8. Fill the `.claims` block with load-bearing claims marked `observed`, `inferred`, `unknown`. If you have fewer than two claims, delete the block.
9. Delete all `FILL` marks and demo text.

## Diagram rules

- `viewBox` 720 wide. Nodes at least 140 wide and 56 high. Grid step 20.
- Up to ~9 nodes. If it does not fit, this is level 3.
- A node is `<g class="node">` with `<rect>` and `<text>`. The main node is `node node--accent`.
- An arrow is `<path class="edge">`. The `#arrow` marker is in the template if you kept its `<defs>`. If you deleted the figure that held `<defs>`, move the marker block into your diagram.
- Put a verb on each arrow: `<text class="edge-label">` such as "calls", "writes to", "returns".
- Give numbers units. "Fast" and "many" do not belong on a diagram.
- Text in nodes is at least 15 units, 3-4 words at most. On a phone the diagram shrinks with its labels, so move long labels into the text under the diagram.
- Take colors only from the template variables. Then the dark theme works by itself.
- The page uses system fonts. For Cyrillic they already have glyphs. The fonts in `assets/fonts` are for video only.
- Below 600 px of screen width the diagram scrolls inside its frame. That is fine. Horizontal scroll of the whole page is an error.
- **Beautiful and to the point.** An even grid, an accent color on the main node and tidy labels: the diagram should please the eye. Remove an element that explains nothing and does not help reading. Do not draw a link with no direction or meaning.

## Check

```bash
python3 <skill-dir>/scripts/check_page.py /tmp/<slug>.html --screenshots /tmp/<slug>-shots
```

- Exit code 0: no external resources, no `FILL` marks, encoding set, size in range.
- Open `wide.png` and `narrow.png` and look at them. Look for text outside blocks, overlapped labels, arrows that miss the target and horizontal scroll on the narrow screen.
- Fix what you find and check again. If Chrome is missing, say so in the answer.

Then save the result by `save.md`.
