#!/usr/bin/env python3
"""Оценка «упрощённого технического русского» (plain-ru).

Эвристика по структурным правилам, вдохновлённым ASD-STE100 и информационным стилем.
Это не проверка соответствия стандарту: словаря нет, проверяется только то, что видно скрипту.

Уровни:
  50  лёгкий   - длина предложения, точка с запятой, пассив, длинные абзацы
  80  обычный  - плюс канцелярит, цепочки отглагольных существительных,
                 причастные и деепричастные обороты, одно действие на предложение,
                 условие перед командой
  100 строгий  - плюс вводные и пустые слова, «является», безличные конструкции

Оценка = доля предложений без нарушений на выбранном уровне.

Запуск:
  ru_score.py [--level 50|80|100] [--json] [ФАЙЛ|-]
  ru_score.py --self-test
"""
from __future__ import annotations

import argparse
import json
import re
import sys

LIMITS = {50: (30, 35), 80: (20, 25), 100: (20, 25)}  # (инструкция, описание)

W = r"[А-Яа-яЁёA-Za-z0-9][А-Яа-яЁёA-Za-z0-9\-]*"

IMPERATIVE_END = ("ите", "йте", "ьте")
IMPERATIVE_WORDS = set("""
открой закрой нажми выбери введи запусти проверь удали добавь установи сохрани скопируй перейди найди
сделай измени замени отправь подожди включи выключи укажи посмотри прочитай запиши создай
""".split())

KANTS = [
    r"осуществ\w*", r"производ(?:ит|ят|ить|ится|ятся)\w*", r"в целях", r"в связи с", r"на сегодняшний день",
    r"в рамках", r"данн(?:ый|ая|ое|ого|ому|ом|ой|ую)", r"посредством", r"имеет место", r"в настоящее время",
    r"в случае если", r"в случае, если", r"с целью", r"по причине", r"в качестве", r"при помощи",
    r"на основании", r"в процессе", r"является", r"являются", r"представляет собой", r"с учётом", r"с учетом",
    r"в части", r"в соответствии с", r"обеспечени\w*", r"реализаци\w*", r"функционировани\w*",
]
KANTS_RE = [re.compile(rf"(?<![А-Яа-яЁё]){k}(?![А-Яа-яЁё])", re.I) for k in KANTS]

VERBAL_NOUN = re.compile(r"(?:ание|ение|яние|тие|ция|ания|ения|яния|тия|ции|анию|ению|анием|ением|ании|ении)$", re.I)

PASSIVE_RE = re.compile(
    rf"\b(?:был|была|было|были|будет|будут)\s+(?:\w+\s+)?\w+(?:ан|ян|ен|ён|т)(?:а|о|ы)?\b", re.I
)
REFLEXIVE_PASSIVE = re.compile(
    r"\b(?:производится|осуществляется|выполняется|проводится|реализуется|производятся|осуществляются|"
    r"выполняются|проводятся|реализуются|создаётся|создается|создаются|формируется|формируются)\b",
    re.I,
)
PARTICIPLE_RE = re.compile(r"\b\w{3,}(?:ющ|ящ|ащ|вш|ем|им)(?:ий|ая|ее|ие|его|ей|их|ую|им|ими|ем)\b", re.I)
GERUND_RE = re.compile(r"(?:^|,\s*)(\w{3,}(?:ав|ив|ыв|ев|вши|ясь|аясь))\b", re.I)
FILLERS = re.compile(
    r"\b(?:как бы|в принципе|на самом деле|собственно|фактически|в общем-то|в общем|достаточно|"
    r"весьма|довольно|определённ\w*|определенн\w*|некотор\w*|различн\w*|многочисленн\w*)\b",
    re.I,
)
IMPERSONAL = re.compile(r"\b(?:необходимо|следует|требуется|нужно|надлежит|рекомендуется)\b", re.I)

CODE_FENCE_RE = re.compile(r"```.*?```", re.S)
INLINE_CODE_RE = re.compile(r"`[^`]*`")
URL_RE = re.compile(r"https?://\S+|file://\S+")


def strip_markup(text: str) -> str:
    text = CODE_FENCE_RE.sub(" ", text)
    text = INLINE_CODE_RE.sub("X", text)
    return URL_RE.sub("URL", text)


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?…])\s+(?=[А-ЯЁA-Z0-9«\"(])", text.strip())
    return [p.strip() for p in parts if re.search(r"[А-Яа-яЁё]", p)]


def paragraphs(text: str) -> list[list[str]]:
    blocks: list[list[str]] = []
    for raw in re.split(r"\n\s*\n", strip_markup(text)):
        lines = [l.strip() for l in raw.splitlines() if l.strip()]
        lines = [l for l in lines if not l.startswith(("#", "|", "<", ">"))]
        if not lines:
            continue
        if all(re.match(r"^([-*+]|\d+[.)])\s+", l) for l in lines):
            for l in lines:
                item = re.sub(r"^([-*+]|\d+[.)])\s+", "", l)
                blocks.append(split_sentences(item) or [item])
        else:
            blocks.append(split_sentences(" ".join(lines)))
    return [b for b in blocks if b]


def words(s: str) -> list[str]:
    return re.findall(W, s)


def is_instruction(s: str) -> bool:
    w = [x.lower() for x in words(s)[:4]]
    if not w:
        return False
    if w[0] in ("если", "когда", "перед", "после", "чтобы"):
        tail = s.split(",", 1)
        return len(tail) == 2 and is_instruction(tail[1])
    if w[0] == "не" and len(w) > 1:
        w = w[1:]
    if w[0].endswith(IMPERATIVE_END) or w[0] in IMPERATIVE_WORDS:
        return True
    # «Открыв файл, нажмите кнопку.» — команда после вводного оборота
    tail = s.split(",", 1)
    if len(tail) == 2:
        first = words(tail[1])[:1]
        return bool(first) and (first[0].lower().endswith(IMPERATIVE_END) or first[0].lower() in IMPERATIVE_WORDS)
    return False


def check_sentence(s: str, level: int) -> list[str]:
    v: list[str] = []
    w = words(s)
    instr = is_instruction(s)
    lim_i, lim_d = LIMITS[level]
    limit = lim_i if instr else lim_d
    if len(w) > limit:
        v.append(f"длинное: {len(w)} слов > {limit} ({'инструкция' if instr else 'описание'})")
    if ";" in s:
        v.append("точка с запятой: разбейте на два предложения")
    m = PASSIVE_RE.search(s) or REFLEXIVE_PASSIVE.search(s)
    if m:
        v.append(f"пассив: «{m.group(0)}» — назовите, кто делает")
    if level >= 80:
        for rx in KANTS_RE:
            k = rx.search(s)
            if k:
                v.append(f"канцелярит: «{k.group(0)}»")
                break
        run, longest = 0, 0
        for tok in w:
            run = run + 1 if (len(tok) > 4 and VERBAL_NOUN.search(tok)) else 0
            longest = max(longest, run)
        if longest >= 2:
            v.append(f"цепочка отглагольных существительных ({longest}) — замените глаголом")
        p = PARTICIPLE_RE.search(s)
        if p:
            v.append(f"причастие: «{p.group(0)}» — лучше «который …» или отдельное предложение")
        g = GERUND_RE.search(s)
        if g and instr:
            v.append(f"деепричастие в инструкции: «{g.group(1)}» — разбейте на шаги")
        if instr:
            body = s.split(",", 1)[1] if s.lower().startswith(("если ", "когда ", "перед ", "после ")) else s
            if re.search(r"\b(?:и затем|, затем|а потом|и потом|после чего)\b", body, re.I) or re.search(
                rf"\bи\s+\w+(?:{'|'.join(IMPERATIVE_END)})\b", body, re.I
            ):
                v.append("два действия: одно действие на предложение")
            if not s.lower().startswith(("если ", "когда ", "перед ", "после ")) and re.search(
                r"\s(?:если|когда|пока не|перед тем как|после того как)\s", s, re.I
            ):
                v.append("условие после команды: начните с условия")
    if level >= 100:
        f = FILLERS.search(s)
        if f:
            v.append(f"пустое слово: «{f.group(0)}»")
        i = IMPERSONAL.search(s)
        if i:
            v.append(f"безличная конструкция: «{i.group(0)}» — скажите, кто делает, или дайте команду")
    return v


def score(text: str, level: int = 80) -> dict:
    blocks = paragraphs(text)
    results, para_issues = [], []
    for i, block in enumerate(blocks):
        if len(block) > 6:
            para_issues.append({"paragraph": i + 1, "sentences": len(block), "rule": "абзац: не больше 6 предложений"})
        for s in block:
            results.append({"sentence": s, "violations": check_sentence(s, level)})
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
        f"plain-ru-{report['level']}: {round(report['score'] * 100)}% "
        f"({report['clean']}/{report['sentences']} предложений без замечаний)"
    ]
    for p in report["paragraphs"]:
        out.append(f"  абзац {p['paragraph']}: {p['sentences']} предложений — {p['rule']}")
    for r in report["violations"]:
        out.append(f"- {r['sentence'][:140]}")
        for x in r["violations"]:
            out.append(f"    * {x}")
    return "\n".join(out)


SELF_TESTS = [
    ("Откройте файл. Удалите старую строку.", 80, 1.0),
    ("Если тест упал, прочитайте лог.", 80, 1.0),
    ("Прочитайте лог, если тест упал.", 80, 0.0),
    ("Откройте файл и удалите старую строку.", 80, 0.0),
    ("Конфигурация была изменена скриптом.", 80, 0.0),
    ("Необходимо осуществить проверку соответствия требованиям.", 80, 0.0),
    ("Скрипт проверяет конфигурацию.", 80, 1.0),
    ("Открыв файл, нажмите кнопку.", 80, 0.0),
    ("Скрипт работает; лог пуст.", 50, 0.0),
    ("Нужно в принципе проверить лог.", 100, 0.0),
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
