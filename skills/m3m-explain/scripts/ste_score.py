#!/usr/bin/env python3
"""Plain-English score: how close a text is to a controlled-English style.

Inspired by ASD-STE100 (Issue 9). This is NOT a compliance checker: it does not
use the ASD dictionary and checks only structural rules that a script can see.

Levels:
  50  light   - long sentences, semicolons, passive voice, long paragraphs
  80  default - adds contractions, phrasal verbs, noun clusters, one instruction
                per sentence, condition before command, marketing words, actions
                hidden in nouns, synonym rotation (one word for one action)
  100 strict  - adds -ing forms, perfect tenses, weak modals, wordy words

Score = share of sentences with no violation at the chosen level.

Usage:
  ste_score.py [--level 50|80|100] [--json] [FILE|-]
  ste_score.py --self-test
"""
from __future__ import annotations

import argparse
import json
import re
import sys

LIMITS = {50: (30, 35), 80: (20, 25), 100: (20, 25)}  # (procedural, descriptive)

IMPERATIVES = set("""
add allow apply ask attach avoid build call cancel change check choose clean clear click close collect commit
compare configure confirm connect copy create cut delete deploy describe disable disconnect do download drag edit
enable enter examine export fill find fix follow get give go hold import inspect install keep kill launch let lift
list load lock log look lower make mark measure merge move note open paste pick point press print pull push put read
record reduce refresh reload remove rename repeat replace reset restart restore return review run save see select
send set show sign sort specify start stop submit switch tell test try turn type uninstall unlock update upgrade
upload use verify view wait wrap write
""".split())

PRONOUN_STARTS = {"i", "you", "we", "they", "he", "she", "it", "this", "that", "these", "those", "the", "a", "an"}

IRREGULAR_PARTICIPLES = set("""
been begun bitten blown born bought broken brought built burnt caught chosen come cut dealt done drawn driven eaten
fallen felt fought found flown forgotten frozen given gone grown held hidden hit hung hurt kept known laid led left
lent let lost made meant met paid put quit read ridden risen run said seen sent set shaken shown shut sold spent
split spoken spread stolen stood struck stuck sung taken taught thought thrown told torn understood won worn written
""".split())

BE_FORMS = r"(?:am|is|are|was|were|be|been|being)"

PHRASAL = [
    ("set|sets|setting", "up"), ("find|finds|finding|found", "out"), ("carry|carries|carrying|carried", "out"),
    ("figure|figures|figuring|figured", "out"), ("point|points|pointing|pointed", "out"),
    ("look|looks|looking|looked", "into|up|over"), ("turn|turns|turning|turned", "on|off"),
    ("shut|shuts|shutting", "down"), ("back|backs|backing|backed", "up"),
    ("go|goes|going|went|gone", "through|over"), ("come|comes|coming|came", "up"),
    ("pick|picks|picking|picked", "up"), ("fill|fills|filling|filled", "in|out"),
    ("check|checks|checking|checked", "out"), ("give|gives|giving|gave|given", "up"),
    ("put|puts|putting", "off|together"), ("take|takes|taking|took|taken", "over|out"),
    ("end|ends|ending|ended", "up"), ("run|runs|running|ran", "into|out"),
    ("break|breaks|breaking|broke|broken", "down"), ("get|gets|getting|got|gotten", "rid|around|back"),
    ("clean|cleans|cleaning|cleaned", "up"), ("spin|spins|spinning|spun", "up"),
    ("wrap|wraps|wrapping|wrapped", "up"), ("hook|hooks|hooking|hooked", "up"),
]
PHRASAL_RE = [re.compile(rf"\b(?:{v})\s+(?:{p})\b", re.I) for v, p in PHRASAL]

CONTRACTION_RE = re.compile(
    r"\b(?:\w+n't|\w+'(?:re|ve|ll|d|m)|it's|that's|there's|what's|here's|let's|who's)\b", re.I
)

FUNCTION_WORDS = set("""
a an the and or but nor so yet for of in on at to from by with without into onto over under about after before
between through during until than then as if when while because although though since unless that which who whom
whose what where why how this these those there here it its i you we they he she them us me my your our their his
her is are was were be been being am do does did done has have had can will must may might should could would not
no all any each every some more most less few many much one two three four five six seven eight nine ten first
next last also only just very too again new old same other such own up down out off
""".split())

MODALS_WEAK = re.compile(r"\b(?:should|could|might|would|may|shall)\b", re.I)
PERFECT_RE = re.compile(r"\b(?:has|have|had)\s+(?:not\s+)?(?:\w+ed|" + "|".join(sorted(IRREGULAR_PARTICIPLES)) + r")\b", re.I)
ING_ALLOW = set("""
thing things nothing something anything everything string strings during bring brings king ring rings spring
sing wing morning evening ceiling building buildings setting settings logging warning warnings heading headings
padding meaning meanings mapping mappings pricing timing routing caching testing parsing rendering hosting tooling
""".split())
WORDY = {
    "utilize": "use", "utilise": "use", "commence": "start", "terminate": "stop", "facilitate": "help",
    "endeavor": "try", "endeavour": "try", "ascertain": "find", "subsequently": "then", "approximately": "about",
    "in order to": "to", "prior to": "before", "in the event that": "if", "due to the fact that": "because",
    "at this point in time": "now", "a number of": "some", "leverage": "use", "implement": "make",
}

# Words that claim quality instead of showing it.
MARKETING_RE = re.compile(
    r"\b(?:seamless(?:ly)?|robust(?:ly)?|effortless(?:ly)?|cutting-edge|state-of-the-art|world-class|best-in-class|"
    r"blazing[- ]fast|game-chang(?:ing|er)|revolutionary|next-generation|supercharge[sd]?)\b",
    re.I,
)
# An action hidden in a noun: "perform an analysis of" -> "analyze".
NOMINAL_RE = re.compile(
    r"\b(?:perform(?:s|ed|ing)?|conduct(?:s|ed|ing)?|carr(?:y|ies|ied|ying) out|undertak(?:e|es|ing)|undertook|"
    r"effect(?:s|ed)?|make(?:s)? an?|made an?)\s+(?:a\s+|an\s+|the\s+)?\w+(?:tion|sion|ment|ance|ence|ysis)\b",
    re.I,
)
# One word for one thing: verbs that writers rotate for the same action.
SYNONYMS = [
    ("check", "verify", "confirm", "validate"),
    ("delete", "remove", "erase"),
    ("start", "launch", "begin", "initiate"),
    ("stop", "halt", "terminate"),
    ("show", "display"),
    ("get", "retrieve", "fetch", "obtain"),
    ("change", "modify", "alter"),
    ("send", "transmit"),
]


def _forms(verb: str) -> str:
    stem = verb[:-1] if verb.endswith("e") else verb
    return rf"(?:{verb}|{verb}s|{verb}d|{verb}ed|{stem}ing|{stem}ed)"


SYNONYM_RE = [[(m, re.compile(rf"\b{_forms(m)}\b", re.I)) for m in g] for g in SYNONYMS]

CODE_FENCE_RE = re.compile(r"```.*?```", re.S)
INLINE_CODE_RE = re.compile(r"`[^`]*`")
URL_RE = re.compile(r"https?://\S+|file://\S+")


def strip_markup(text: str) -> str:
    text = CODE_FENCE_RE.sub(" ", text)
    text = INLINE_CODE_RE.sub("X", text)
    text = URL_RE.sub("URL", text)
    return text


def paragraphs(text: str) -> list[list[str]]:
    """Split into blocks. Each block is a list of sentence strings."""
    blocks: list[list[str]] = []
    for raw in re.split(r"\n\s*\n", strip_markup(text)):
        lines = [l.strip() for l in raw.splitlines() if l.strip()]
        lines = [l for l in lines if not l.startswith(("#", "|", "<", ">"))]
        if not lines:
            continue
        is_list = all(re.match(r"^([-*+]|\d+[.)])\s+", l) for l in lines)
        if is_list:
            for l in lines:
                blocks.append(split_sentences(re.sub(r"^([-*+]|\d+[.)])\s+", "", l)) or [l])
        else:
            blocks.append(split_sentences(" ".join(lines)))
    return [b for b in blocks if b]


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(])", text.strip())
    return [p.strip() for p in parts if re.search(r"[A-Za-z]", p)]


def words(sentence: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9][A-Za-z0-9'\-./_]*", sentence)


def is_procedural(sentence: str) -> bool:
    w = [x.lower() for x in words(sentence)[:3]]
    if not w:
        return False
    if w[0] in ("do", "don't") and len(w) > 1 and w[1] == "not":
        return True
    if w[0] in ("if", "when", "before", "after", "unless"):
        # "If X, do Y." -> look after the first comma
        tail = sentence.split(",", 1)
        return len(tail) == 2 and is_procedural(tail[1])
    return w[0] in IMPERATIVES


def check_sentence(s: str, level: int) -> list[str]:
    v: list[str] = []
    w = words(s)
    proc = is_procedural(s)
    lim_p, lim_d = LIMITS[level]
    limit = lim_p if proc else lim_d
    if len(w) > limit:
        v.append(f"long: {len(w)} words > {limit} ({'procedure' if proc else 'description'})")
    if ";" in s:
        v.append("semicolon: split into two sentences")
    passive = re.search(rf"\b{BE_FORMS}\s+(?:\w+ly\s+)?(\w+ed|" + "|".join(IRREGULAR_PARTICIPLES) + r")\b", s, re.I)
    if passive and not re.search(r"\b(?:used to|supposed to|based on)\b", s, re.I):
        v.append(f"passive: '{passive.group(0)}' - say who does it")
    if level >= 80:
        c = CONTRACTION_RE.search(s)
        if c:
            v.append(f"contraction: '{c.group(0)}'")
        for rx in PHRASAL_RE:
            m = rx.search(s)
            if m:
                v.append(f"phrasal verb: '{m.group(0)}' - use one verb")
                break
        run, longest = 0, 0
        for tok in w:
            t = tok.lower()
            content = (t not in FUNCTION_WORDS and "'" not in t and not t.endswith(("ly", "ed", "ing"))
                       and not t[0].isdigit())
            run = run + 1 if content else 0
            longest = max(longest, run)
        if longest >= 4:
            v.append(f"noun cluster: {longest} words in a row - max 3")
        m = MARKETING_RE.search(s)
        if m:
            v.append(f"marketing word: '{m.group(0)}' - delete it or give the number that proves it")
        m = NOMINAL_RE.search(s)
        if m:
            v.append(f"action as a noun: '{m.group(0)}' - use the verb")
        if proc:
            body = s.split(",", 1)[1] if s.lower().startswith(("if ", "when ", "before ", "after ", "unless ")) else s
            if re.search(r"\b(?:and then|, then|then)\s+[a-z]+", body) or re.search(
                r"\band\s+(" + "|".join(IMPERATIVES) + r")\b", body
            ):
                v.append("two instructions: one instruction per sentence")
            if not s.lower().startswith(("if ", "when ", "before ", "after ", "unless ")) and re.search(
                r"\s(?:if|when|unless|before|after)\s", s
            ):
                v.append("condition after command: put the condition first")
    if level >= 100:
        for tok in w:
            t = tok.lower()
            if t.endswith("ing") and len(t) > 4 and t not in ING_ALLOW:
                v.append(f"-ing form: '{tok}'")
                break
        if PERFECT_RE.search(s):
            v.append("perfect tense: use simple past or present")
        m = MODALS_WEAK.search(s)
        if m:
            v.append(f"weak modal: '{m.group(0)}' - use can, will or must")
        low = s.lower()
        for bad, good in WORDY.items():
            if re.search(rf"\b{re.escape(bad)}\b", low):
                v.append(f"wordy: '{bad}' -> '{good}'")
                break
    return v


def score(text: str, level: int = 80) -> dict:
    blocks = paragraphs(text)
    results = []
    para_issues = []
    for i, block in enumerate(blocks):
        if len(block) > 6:
            para_issues.append({"paragraph": i + 1, "sentences": len(block), "rule": "paragraph: max 6 sentences"})
        for s in block:
            results.append({"sentence": s, "violations": check_sentence(s, level)})
    if level >= 80:
        first: dict[int, str] = {}
        for r in results:
            for gi, group in enumerate(SYNONYM_RE):
                for member, rx in group:
                    if rx.search(r["sentence"]):
                        if gi not in first:
                            first[gi] = member
                        elif first[gi] != member:
                            r["violations"].append(
                                f"synonym rotation: '{member}' after '{first[gi]}' - use one word for one action"
                            )
                        break
    total = len(results)
    clean = sum(1 for r in results if not r["violations"])
    value = clean / total if total else 1.0
    if para_issues and total:
        value = max(0.0, value - 0.05 * len(para_issues))
    return {
        "level": level,
        "score": round(value, 3),
        "sentences": total,
        "clean": clean,
        "violations": [r for r in results if r["violations"]],
        "paragraphs": para_issues,
    }


def render(report: dict) -> str:
    out = [
        f"plain-{report['level']} score: {round(report['score'] * 100)}% "
        f"({report['clean']}/{report['sentences']} sentences clean)"
    ]
    for p in report["paragraphs"]:
        out.append(f"  paragraph {p['paragraph']}: {p['sentences']} sentences - {p['rule']}")
    for r in report["violations"]:
        out.append(f"- {r['sentence'][:140]}")
        for x in r["violations"]:
            out.append(f"    * {x}")
    return "\n".join(out)


SELF_TESTS = [
    ("Open the file. Remove the old line.", 80, 1.0),
    ("If the test fails, read the log.", 80, 1.0),
    ("The configuration was changed by the script.", 80, 0.0),
    ("Read the log if the test fails.", 80, 0.0),
    ("Open the file and remove the old line.", 80, 0.0),
    ("Don't set up the server; it's broken.", 50, 0.0),
    ("We utilize the cache.", 100, 0.0),
    ("We use the cache.", 100, 1.0),
    ("```\nthis code is ignored; was written by me\n```\nRun the tests.", 80, 1.0),
    ("Our seamless pipeline deploys the app.", 80, 0.0),
    ("Perform an analysis of the log.", 80, 0.0),
    ("Check the log. Verify the config.", 80, 0.5),
    ("Check the log. Check the config.", 80, 1.0),
    ("The request may have failed.", 80, 1.0),
]


def self_test() -> int:
    failed = 0
    for text, level, expected in SELF_TESTS:
        got = score(text, level)["score"]
        ok = abs(got - expected) < 1e-6
        failed += 0 if ok else 1
        print(f"{'ok  ' if ok else 'FAIL'} level={level} expected={expected} got={got} :: {text[:50]!r}")
    print("all passed" if not failed else f"{failed} failed")
    return 1 if failed else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", nargs="?", default="-")
    ap.add_argument("--level", type=int, choices=[50, 80, 100], default=80)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    text = sys.stdin.read() if a.file == "-" else open(a.file, encoding="utf-8").read()
    report = score(text, a.level)
    print(json.dumps(report, ensure_ascii=False, indent=2) if a.json else render(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
