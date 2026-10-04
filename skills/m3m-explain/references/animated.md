# Level 3: HTML page with animation or interaction

Karpathy: "ask for output in HTML to get a beautiful, interactive webpage… animations". The goal is a beautiful page that shows how the thing works. The reader needs several linked pictures of one model. Build the page by all the steps of `diagram.md` and its diagram rules. There is one difference: in step 5, keep the components you need. Delete the others. If you do not need the slider, delete the `window.onSlider` demo.

## Choose the interaction

Take every interaction that makes the model clearer. Often there are two: a step player and a slider, or a path switch and details. The template is a starting point. If the topic needs its own visualization (a chart, a canvas animation, a live simulation), build it.

| Interaction | When | Template component |
|---|---|---|
| Step player | A process, a loop, an object that changes form | `figure.stepper` |
| "What if" slider | The result depends on a parameter | `input[data-slider]` |
| Path switch | The normal path and the failure path on one diagram | `data-path` buttons |
| Overview and details | Not every reader needs the details | `<details>` |

Each element answers a reader's question. Showiness is a plus when it shows how the thing works. Delete an element that explains nothing.

## Step player

- One concrete example runs through all steps. Each step shows what changed.
- The shared background of the diagram sits outside the `.step` groups.
- Each frame is `<g class="step" data-step="N">`, numbered from 1. Frame N shows together with all frames before it. So put in a frame only what appeared at that step.
- The note for a frame is `<div class="step-note" data-step-note="N">`, one or two sentences: what changed and why. If the example is text or code (tokens, JSON, an address), show it in the note as a `<pre>` block.
- Small elements inside the example (tokens, fields) may be smaller than nodes.
- The player diagram is at most ~520 units high. The buttons sit under the diagram and must fit a laptop screen.
- The buttons ←, ▶, → and the keyboard arrows already work. The address `#step=N` or `#step=last` opens the needed frame.
- Usually 3-8 steps. If you need more, split the explanation into overview and details.

## Slider

- Define `window.onSlider = function (value) { ... }` in your script. The function gets a number and changes the diagram: a bar width, a point position, a result label.
- Label the parameter and its units. Take the `min`/`max` range from the real meaning.
- Compute the numbers in labels with the same formula as in the explanation.

## Path switch

- Elements of the normal path get the class `only-normal`, elements of the failure path get `only-failure`. Shared elements get no class.
- The inactive path fades, and the shared parts stay in place. This way the reader compares paths on one diagram.

## Motion

- The player steps fade in smoothly. That is already in the template. Build your own motion with CSS `transition`, WAAPI or canvas, so the reader sees one state turn into another.
- Motion shows the mechanism: a data path, growth of a value, a change of form.
- With `prefers-reduced-motion`, motion stops. Steps and states stay.
- Loops and autoplay are fine if the reader can stop them with a button.

## Check

```bash
python3 <skill-dir>/scripts/check_page.py /tmp/<slug>.html --screenshots /tmp/<slug>-shots --steps
```

Check everything from `diagram.md`. The frames `step-first.png` and `step-last.png` must differ and show the start and the end of the example. Then save the result by `save.md`.

## Next step

At the end of the answer, offer a video on the same topic in one line. Example: "I can make a 3Blue1Brown-style video explainer. The build takes ~15-25 minutes. Do it?" If the user agrees, work by `video.md`.
