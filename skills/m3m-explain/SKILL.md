---
name: m3m-explain
description: "Use when the user wants to understand something, not change it: explain, how does X work, what is, why, walk me through, I don't get it, show me visually, «объясни», «как работает», «что такое», «не понял». Covers a concept, code, architecture, an article, a link or a previous answer."
---
# m3m-explain: the explanation ladder

Karpathy's idea: models do more work, so our job becomes understanding their output. For hard material, each step up is "even better". The ladder has four steps: text, diagram, page, video.

`<skill-dir>` is the folder that holds this SKILL.md. All paths below start from it.

## Steps

1. **Question.** Decide what the user must understand. Ask only when two readings give different explanations.
2. **Model.** Read the source: the code, the diff, the article or the logs. Name 2-5 load-bearing parts and their links. Mark key claims observed, inferred or unknown.
3. **Reader.** If the reader shows no prior knowledge, start simple and carry one example through every step. If the reader knows the topic, go to links, causes and failures.
4. **Level.** Use text for a simple fact, a definition, a single cause, a command to copy, a yes/no answer or an explicit text format. For hard material, climb until the next step makes understanding better. When in doubt, go one step up. See `references/ladder.md`.

| Difficulty | Level | Reference |
|---|---|---|
| Simple fact, definition, single cause, command | 1. Text | `references/text.md` (Russian: `references/text-ru.md`) |
| One link that is easier to see: order, cause, dependency | 2. HTML diagram | `references/diagram.md` |
| Steps, paths, states, a system; an example changes form; the result depends on a parameter | 3. Animated HTML page | `references/animated.md` |
| The core is motion or transformation; the topic suits a 3Blue1Brown-style video | 4. Video | `references/video.md` |

   If the model has two forms, take the higher level. Put the lower forms inside it.
5. **Video is the main form, but always through a question.** For level 4, ask before you build. After a level 3 page, offer a video in one line. If the user asks for a video, skip the question. Workflow: `references/video.md`.
6. **An explicit format sets the level exactly, not as a minimum.** "In 5 sentences" means text of exactly five sentences. "Draw it" or "diagram" means level 2. "Make a page" means level 3. "Video" means level 4. Do not go above it. Offer the next step in one line.
7. **Announce the choice** in the first line: "Level 3: the example changes form at each step, so it is easier to walk through."
8. **"I don't get it"** after an explanation: go up exactly one step. Change the medium, not the wording.
9. **Output of the model itself.** Explaining a diff, PR, plan or "why did you do X" is the main case. Same ladder. A request to fix something ("fix it", "why does the test fail" during debugging) is not an explanation. Do not use this skill.
10. **Environment.** If the environment cannot do the level (no shell, browser or video tools), give the nearest form with the same structure. Name the missing level in one line.

## Language, text and checks

Reply in the language of the request. English: write by `references/text.md` and check with `python3 <skill-dir>/scripts/ste_score.py --level 80 -` (threshold 0.8). Russian: write by `references/text-ru.md` and check with `python3 <skill-dir>/scripts/ru_score.py --level 80 -`. Build level 2 and 3 pages from `assets/page.html`. Check them with `scripts/check_page.py`.

## Chat reply

- Level 1: the level line and the explanation.
- Levels 2-4: the level line, a 2-4 sentence answer, load-bearing points as a list, file paths. End with one line that names what you could not verify.
- After level 3: a line that offers a video.

## Saving

Save each explanation as `references/save.md` says. After a successful write, say "saved". Not before.
