# Level 4: video through HyperFrames

Karpathy considers the video explainer the strongest form: "the output format I am most bullish on", "a 3b1b style video explainer on X". HyperFrames builds the video by the faceless-explainer workflow. The video has no voice and no music. Built-in sound effects play. Visual math and short theses on screen carry the meaning.

## 1. The question

Video starts in one of two ways. Ask before the build when the core of the topic is motion or transformation. Or offer it in one line after a level 3 page. If the user did not ask for a video explicitly, ask one question (AskUserQuestion, if you have it): "I suggest a video explainer in the style of 3Blue1Brown, because <reason>. About 60 s, build takes 15-25 minutes."
Options:

- "Build and render".
- "Preview first".
- "No, make an HTML animation": then level 3 by `animated.md`.

The answer also counts as the consent to render that HyperFrames requires. An explicit request such as "make a video" cancels the question: it is already consent to build and render.

## 2. Check the environment

Check by exit code, not by file presence: a broken binary passes `which`.

```bash
node -e 'process.exit(Number(process.versions.node.split(".")[0]) >= 22 ? 0 : 1)' || echo "MISSING: node 22+"
ffmpeg -hide_banner -version >/dev/null 2>&1 || echo "MISSING: working ffmpeg"
ffprobe -hide_banner -version >/dev/null 2>&1 || echo "MISSING: working ffprobe"
(for s in hyperframes faceless-explainer media-use; do python3 <skill-dir>/scripts/find_skill.py "$s" >/dev/null 2>&1 || exit 1; done) || echo "MISSING: HyperFrames skills (hyperframes, faceless-explainer, media-use)"
npx hyperframes browser path >/dev/null 2>&1 || echo "MISSING: Chrome for rendering"
```

If any line "MISSING: …" prints, do not make the video. Build level 3 and name what is missing in one line: "no working ffmpeg". Install nothing without consent: `browser path` only looks for Chrome and downloads nothing.

## 3. Launch rules

- Do not run `npx hyperframes skills update` without the user's consent.
- Do not write preferences through `prefs.mjs`: this is a one-off explanation.
- Do not run the faceless-explainer gates about `prefs.mjs`, `skills update` and entry through `/hyperframes`. This skill skips them on purpose. It is not an error.
- `<slug>` follows `save.md`, section 1.
- Working folder: `~/.cache/m3m-explain/<slug>/`. Project: `videos/<slug>` inside it.
- Skill folders, used below:

```bash
F="$(python3 <skill-dir>/scripts/find_skill.py faceless-explainer)/scripts"
FE="$(python3 <skill-dir>/scripts/find_skill.py faceless-explainer)"
H="$(python3 <skill-dir>/scripts/find_skill.py hyperframes)"
MU="$(python3 <skill-dir>/scripts/find_skill.py media-use)"
```

## 4. Build order

Follow the steps of `$FE/SKILL.md` with the differences below. The mode is autonomous. Do not ask checkpoint questions. Post a short summary instead.

1. `npx hyperframes init "videos/<slug>" --non-interactive --example=blank --skill=faceless-explainer`
2. `BRIEF.md` by `$H/references/brief-format.md`: `workflow: faceless-explainer`, `flow: automation`, `storyboard: no`, `message`, `destination: youtube`, `aspect: 1920x1080`, `language:` the language of the request, `length: 60s`, `angle: concept`. In `## Notes`: `narration: no`, `music: none`.
3. `npx hyperframes auth status`: show the output and continue offline. Exit code 1 without a HeyGen login is normal.
4. `capture/extracted/visible-text.txt` is the model of the topic and the source. `capture/extracted/tokens.json` is `{"title": "...", "description": "...", "colors": [], "fonts": []}`.
5. `node $F/build-frame.mjs --preset <preset> --hyperframes .`: any preset, because section 7 (3Blue1Brown style) sets the frame palette anyway. In `frame.md`, add `canvas: "#0e0e10"` as the first key in `colors`, so the build background matches the frames.
6. Font: `mkdir -p assets/fonts && cp <skill-dir>/assets/fonts/*.woff2 assets/fonts/`. The built-in HyperFrames fonts do not cover Cyrillic (tested).
7. `STORYBOARD.md` by `$H/references/storyboard-format.md` and section 6 below. Do not create `SCRIPT.md`.
8. `node $F/audio.mjs --script ./SCRIPT.md --storyboard ./STORYBOARD.md --hyperframes . --out ./audio_meta.json`: expect "project marked silent".
9. `node $F/audio.mjs fetch-sfx --storyboard ./STORYBOARD.md --hyperframes .`: **required**. In silent mode faceless-explainer skips this step, and there will be no sounds. Then place sounds on events inside frames: `python3 <skill-dir>/scripts/sfx_offsets.py --storyboard ./STORYBOARD.md --audio-meta ./audio_meta.json`.
10. Frames `compositions/frames/NN-<name>.html` by the contract `$H/references/frame-worker-core.md` and section 7 below. Build the frames yourself, without subagents: the worker contract forbids explanation text on screen. Reduce step 4 of faceless-explainer to one thing: each frame in `STORYBOARD.md` has a scene with timing. The status of finished frames is `animated`.
11. `node $F/assemble-index.mjs --storyboard ./STORYBOARD.md --hyperframes .`: in the output, `sfx (track 20+)` is above zero.
12. `node $F/transitions.mjs inject --storyboard ./STORYBOARD.md --hyperframes .` and `node $F/transitions.mjs verify --storyboard ./STORYBOARD.md --index ./index.html`.
13. `npx hyperframes lint` and `npx hyperframes check`: 0 errors. Then `npx hyperframes snapshot --at <midpoints of all frames>` and look at the contact sheet. After fixes, repeat the snapshot at all midpoints: it overwrites the sheet.
14. If the user chose "Preview first": `npx hyperframes preview --background`, and wait for the reply.
15. `npx hyperframes render --skill=faceless-explainer --quality high --output renders/video.mp4`.

## 5. Sound

In the top YAML of `STORYBOARD.md`: `music: none`. Frames have an `sfx:` field with names from the built-in library `$MU/audio/assets/sfx/`:

| Name | When |
|---|---|
| `whoosh`, `whoosh-short` | fast appearance, scene change |
| `whoosh-cinematic` | wide transition: builds from ~1 s, peaks at ~2.6 s, quiet after ~4 s |
| `pop` | an element, mark or node appears |
| `click`, `click-soft` | switch, choice |
| `chime` | correct answer, result |
| `ping` | key number or conclusion |
| `sparkle` | highlight of the main element |
| `impact-bass-1`, `impact-bass-2` | thesis, strong point |
| `riser` | build-up to a climax: builds from ~1 s, loud ~2.8-4.0 s, then silence (the file is 10 s long) |
| `typing`, `key-press` | typing text or code |
| `notification` | message, event |
| `error` | failure, wrong path |
| `glitch-1`, `glitch-2`, `glitch-3` | sharp failure, distortion |

Put a sound on an event: a node appears, a point jumps, a formula comes together. In the frame set `sfx: pop, chime` and `sfx_at: 1.2, 4.5`: seconds from the start of the frame, in the order of the sounds. Without `sfx_at`, the sound plays at the start of the frame. Usually 1-2 sounds per frame. For `riser` and `whoosh-cinematic`, place `sfx_at` so the loud part lands on the event: a riser that should hit at second T starts at about T - 4. The same sound can repeat in one frame (`sfx: pop, pop, pop`), with one `sfx_at` value per mention. Some files start with silence: `chime` 0.42 s, `ping` 0.31 s, `error` 0.61 s. Subtract it from `sfx_at`, or the sound will come late.

## 6. Story

- Length 30-90 s, 5-9 frames. `length` in the brief is a guide: if the duration rule below gives more, keep that. The thesis sounds no later than the second frame.
- Do not start with a definition. Start with a question or a contradiction.
- 3-6 ideas. One idea per frame. Intuition first, then formalism.
- Each motion carries a task: transformation, order, change of state, data path, geometry, time or cause. Slides made of paragraphs are not video.
- Video fits any hard topic, not only physics. For a mechanism or a system, look for what motion can show. Examples: the path of a request, growth of a value, the assembly of a formula.
- Structure and techniques: `$FE/references/story-design.md`.
- A frame in `STORYBOARD.md`: `scene`, `duration`, `transition_in`, `status`, `sfx`, `src`, `onscreen` (text on screen). Leave the `voiceover` field empty.
- Frame duration follows reading time: words of on-screen text / 2.5 + 1 s, at least 4 s. Count a number or a formula sign as a word. If the frame has important motion, add its duration. Round up to 0.5 s.

## 7. Frames in the 3Blue1Brown style

The picture carries the meaning, not the text. Text is short theses that name what you see.

- **Background and colors.** Background `#0e0e10`. 3Blue1Brown colors: blue `#58C4DD`, yellow `#FFFF00`, brown `#CD853F`, green `#83C167`, red `#FC6255`, text `#ECECEC`. Each quantity has its own color, and it does not change from frame to frame.
- **Visual math.** Axes, graphs, vectors, points on a curve, areas under a curve, all in SVG. Build a formula in parts. Each part appears with its meaning in the picture. Each part has the color of its quantity.
- **Transformation instead of slide changes.** An object changes form before the eyes: a point slides along a curve, a vector turns, a shape deforms. Animate SVG attributes through GSAP (`attr`, `x`, `y`, `scale`, `rotation`). Draw a line with `strokeDasharray` and `strokeDashoffset` equal to the real path length (`getTotalLength()`). With `pathLength="1"` the GSAP offset does not scale, and the line is visible at once.
- **Camera.** A slow push-in or shift to an important detail, with no hard cuts inside an idea.
- **Text.** There is no voice, so the thesis of the explanation stands on screen: 3-8 words, with the rules from `text.md` (for Russian, `text-ru.md`). A caption appears together with what it names.
- In the `<style>` of each frame, insert the content of `<skill-dir>/assets/fonts/fontface.css`. For all text use `font-family: "Explain Sans"`. Do not use the preset fonts in frames.
- The font has no arrows (→, ←), no ≈ sign and no Greek letters. Draw arrows in SVG. Replace Greek letters with words: "learning rate" instead of η.
- Start ids and classes with a letter: `f02-title`, not `02-title`. Otherwise the selector breaks.
- Each `class="clip"` has its own `id`.
- A second `fromTo` on the same element needs `immediateRender: false`.
- If `check` complains about contrast, take the color it suggests.

## 8. Check and delivery

1. `ffprobe -v error -show_entries stream=codec_type -of csv=p=0 renders/video.mp4` → `video` and `audio`.
2. Duration: `ffprobe -v error -show_entries format=duration -of csv=p=0 renders/video.mp4`.
3. Pull 3-4 frames: `ffmpeg -v error -y -ss <t> -i renders/video.mp4 -frames:v 1 <png>`. Look at them. The text must be readable. Cyrillic must show no boxes. Nothing may be cut off.
4. Copy `renders/video.mp4` into the working folder as `~/.cache/m3m-explain/<slug>/<slug>.mp4`. Save it by `save.md`.
5. In the answer: the path to the mp4, the real duration, the contact sheet. Do not call the video done until the render has finished.
