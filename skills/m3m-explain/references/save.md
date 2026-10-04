# Saving the explanation

If you are in a git repository, save every explanation in the project. Outside a repository, save to `~/explanations/`. The user does not need to ask.

## 1. Name

`<Topic>` is the core of the question in 2-5 words, without "explain" or "about how". Example: "Make a video about how a cache works" becomes "How a cache works".

`<slug>` is `<Topic>` in kebab-case Latin letters: lowercase, words joined by hyphens, no date. Example: "How a cache works" becomes `how-a-cache-works`.

For a Cyrillic topic, transliterate with this table: а-a б-b в-v г-g д-d е-e ё-e ж-zh з-z и-i й-y к-k л-l м-m н-n о-o п-p р-r с-s т-t у-u ф-f х-kh ц-ts ч-ch ш-sh щ-shch ъ — skip, ы-y ь — skip, э-e ю-yu я-ya. Example: «Как работает кэш» becomes `kak-rabotaet-kesh`.

## 2. Folder and name check

Target folder:

- Inside a git repository: `<root>/explanations/<slug>`. `<root>` is the output of `git rev-parse --show-toplevel`.
- Otherwise: `~/explanations/<slug>`.

Check that the folder does not exist: `test -e <path>`. If it exists, do not overwrite anything. Ask the user for another name. If you cannot ask (a run with no dialog), add the date and time to the slug: `-YYYYMMDD-HHMM`. Then use the same name everywhere.

## 3. Write

If the base folder is missing, create it. Create the topic folder without `-p`, so an existing folder fails:

```bash
mkdir -p "<base>" && mkdir "<base>/<slug>"
```

Here `<base>` is `<root>/explanations` or `~/explanations`.

- Level 1: write the note `<slug>.md` into the folder.
- Levels 2-4: copy `<slug>.html` or `<slug>.mp4` into the folder. You may add a short note `<slug>.md` next to it.

A note has this form:

- The first line is `# <Topic>`.
- "Question:" is the user's request.
- "Level:" is the number and the reason in one phrase.
- Then the explanation text: the full text for level 1, the answer and the load-bearing points for levels 2-4. For a file, link it: `[<slug>.html](<slug>.html)`.

Write the note with overwrite protection (`set -C` in shell or mode `x` in Python).

Do not add the files to git. Do not commit them. The user decides that.

## 4. Errors

Say "saved" only after a successful write. If the write failed, still give the explanation and name the error honestly.
