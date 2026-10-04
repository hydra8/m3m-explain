# The explanation ladder

## Karpathy's idea

Source: Andrej Karpathy's post of October 2, 2026, https://x.com/karpathy/status/2105819303471976479. What follows is a retelling.

Language models work better and do more by themselves. Human work moves up, toward oversight and understanding of their output. Models help here too.

Intelligence and code are now cheap. So you can order a large one-off artifact for a single question: a web app or a video for one reader. Before, such an artifact did not pay off.

Karpathy names four forms. He adds each next one with the words "even better":

1. **Text** in ASD-STE100, the controlled language of aviation technical documentation. Its rules give clean text. The standard is strict, so Karpathy sometimes softens it: "80% of the way to ASD-STE100".
2. **Diagram** instead of text. A diagram is easier to take in and understand.
3. **Web page:** the answer "in HTML", beautiful and interactive, with animation.
4. **Video explainer** on any topic, for example in the style of 3Blue1Brown. Karpathy is most bullish on this form.

His advice: test the limits boldly, and the result will surprise you.

## Rule for choosing

The ladder is for hard material. A simple fact, a definition, a single cause or a copy-paste command is text. For everything else, climb until the next step makes understanding better.

- Each next step is "even better". Do not stop at "already clear". Ask yourself: is one more step up clearer?
- The artifact is cheap and one-off. When in doubt, take the higher step.
- A long text from which the reader must assemble the picture is expensive for the reader, even if it is cheap to write.
- Beauty is part of the goal. A beautiful animated page beats a dry one when the animation shows how the thing works.

| Step | Where it works best |
|---|---|
| Text | Definition, fact, single cause, command. The reader holds the answer in mind after one reading |
| Diagram | One link that is easier to see: order, hierarchy, dependency, cause, state |
| Web page | Several linked pictures of one model: steps, paths, states, overview and details, dependence on a parameter |
| Video | Motion or transformation that is better to watch than to scroll. Any hard topic, if the user agrees to wait for the build |

## Shape of the difficulty

| Difficulty | The reader needs to | Usual step |
|---|---|---|
| Definition, property, single cause | Read once | Text |
| One link: order, dependency, nesting, cause, state | See one picture | Diagram. Page, if the link depends on a parameter |
| Transformation by stages: one input changes form several times | Follow one example through all stages | Page with steps |
| Change over time in steps: state, feedback, repetition | See the state before and after each step | Page with steps |
| Continuous motion: rotation, oscillation, wave, flow, smooth deformation | See the path and speed itself | Video |
| Geometry, position | See what is where and how far | Diagram. Page, if the reader changes a parameter. Video, if the point is the motion of a shape |
| Several levels of abstraction | Move from overview to detail | Page |
| A system of interacting parts | See the map and follow one request through it | Page |
| Two paths through the same parts: normal and failure | Compare the paths on one diagram | Page |
| Several points of view on one thing | Compare them line by line | Table in text. Page, if each needs its own picture |

If the model has two forms, take the higher step and use the lower one inside it.

In a sequence diagram, nodes are participants and messages are arrows. Use a page with steps when the reader must follow the exchange step by step. If one look at the arrows is enough, use a diagram.

## Video

Karpathy considers video the strongest form. The build takes 15-25 minutes, so video always needs the user's say:

- If the core of the model is motion or transformation, ask before the build ("level 4").
- After a level 3 page, offer a video on the same topic in one line.
- An explicit video request cancels the question.

The page player shows discrete steps that the reader looks at one by one. Video adds what a page lacks: continuous motion, rhythm and visual math in the style of 3Blue1Brown.

## Output of the model itself

Explaining what the model did is Karpathy's main case. A diff, a PR, a plan, a run log, "why did you do X" are all explanations. The ladder is the same: a short change is text, links between steps of the work are a diagram, a large change across many files is a page with a map of changes and the path of one request.

A request to fix something is not an explanation. "Fix it", "why does the test fail" or "why is CI red" during debugging need debugging. Do not use this skill.

## Hints for the "I am learning" mode

A beginner has no picture on which the words can land. Lean toward a page if several of these hold:

- the explanation carries one object through changes of representation.
- each stage takes the output of the previous one, and there are more than three stages.
- the mechanism has several levels, and the reader must link them.
- state changes over time, or a loop feeds the result back to the input.
- a cause at one stage gives an effect several stages later.
- position, distance or geometry carry part of the idea.

## Hints for systems

Lean toward a page when several of these hold:

- more than three important parts interact, or several layers of the system matter.
- you must explain both the normal flow and the failure flow.
- the reader moves from overview to detail.
- state changes, a timeline or data origin carry part of the model.
- trust or permission boundaries matter.
- the answer needs two diagrams or two views of one system.
- the explanation carries one request through the system or one failure through the parts.
- the reader will probably come back to it.

## Reasons that do not decide the step

These statements hold for many topics that still need a page:

- nothing needs input from the reader.
- there are no controls.
- Markdown can technically hold the same information.
- the steps can be written as a numbered list.
- the request is short or the topic has a single name.

## Calibration

| Topic | Usual step |
|---|---|
| "Why is the sky blue?", "What is a mutex?", "What does commutativity mean?", "Why the Cache-Control header?", "what does this regex do?" | Text |
| A cache between app and database, a three-stage CI, "draw the folder structure", task dependencies in a sprint | Diagram |
| SSH key login step by step, how JPEG compresses an image, how a transformer turns tokens into probabilities, a queue with retries and dead letters, how batch size changes speed and memory, an agent run log with three retries and a rollback | Page; then offer a video |
| How a pendulum trades energy, how an orbit follows from gravity, how a convolution slides over an image | Video through a question |

The examples show shapes. Decide by the shape of your own model, not by likeness to an example.

## When text stays text

The step does not grow if at least one of these holds:

- there is no difficulty: a simple fact, definition or single cause.
- the reader needs exact numbers or commands to copy.
- the answer is "yes" or "no".
- the user explicitly asked for a text format.

## "I don't get it": change the medium

Repeating the explanation with the same means is almost always a mistake. It assumes the words are at fault. More often the model does not fit the current form. So when the reader says "I do not get it", go up exactly one step.

Exception: if the reader does not know the words, rather than failing to hold the structure, rewrite the text by `text.md`.

## The main mistake: staying low

A correct answer can still fail if its form makes the reader assemble the picture. Examples: a long text about a many-stage mechanism. Several unrelated diagrams instead of one page. A normal and a failure path that the reader must compare alone. A page where a video would show the motion.

Noise is also a mistake. Remove an animation or a control that explains nothing. Keep the beauty when it shows how the thing is built.

## Explicit format

An explicit request for form, length or format outranks these rules and sets the level exactly, not as a minimum:

- "In five sentences", "briefly", "as text": text.
- "Draw", "diagram": level 2, one diagram.
- "Make a page", "interactive": level 3.
- "Video", "clip": level 4.

Do not go above the explicit format. If the topic needs more, do the task and offer the next step in one sentence.
