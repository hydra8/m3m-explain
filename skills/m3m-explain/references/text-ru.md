# Text in Russian: plain-ru-80 and level 1

Use this file when the user writes in Russian. Instructions are in English. Examples stay in Russian.

## Where the rules come from

Karpathy asks for explanations in ASD-STE100 and sometimes softens the request: "80% of the way to ASD-STE100", because "the spec is quite stringent". He says nothing more about the 80%.

ASD-STE100 exists only for English. For Russian text this skill carries over the STE rules (2-5, 10 and 11 below), adds rules against typical Russian problems (6-9) and the information-style rule "answer first" (1). The rule set and the name plain-ru-80 follow the legible skill (oshnilia/claude-plugins). This is a house style, not compliance with the standard. Never call a text "ASD-STE100 compliant".

Soften the way Karpathy does: keep structural rules strict, keep the vocabulary softer (terms, a rare passive and one or two comparisons are fine). This reading comes from output-form-ladder. Karpathy does not state it.

## Rules (plain-ru-80)

They apply to everything a human reads: chat answers, diagram labels, page text, on-screen text in videos.

1. Сначала ответ, потом причины.
2. Описание — до 25 слов. Инструкция — до 20 слов.
3. Одно действие или одна мысль в предложении.
4. Условие перед действием: «Если тест упал, прочитайте лог».
5. Действительный залог. Назовите, кто делает: «Скрипт изменил конфиг».
6. Глагол вместо отглагольного существительного: «проверить», а не «осуществить проверку».
7. Без цепочек на «-ние» и «-ция».
8. Без канцелярита: «является», «данный», «в рамках», «в целях», «посредством», «осуществлять».
9. Без причастных и деепричастных оборотов в инструкциях.
10. Без «;». Абзац — одна тема, не больше 6 предложений.
11. Один термин — одно значение во всём тексте. Объясните термин при первом упоминании. Код и английские термины оставьте как есть.

Honesty comes before simplicity:

- Mark inference and unknowns in the same sentence: «вероятно», «источник этого не говорит». Say what would settle the question.
- Write your own design as a recommendation with a condition: «Если задачи должны возобновляться, журнал событий должен быть главным источником».
- Mark an invented example as an illustration.
- Do not swap a technical term for a simple but wrong word. Give the exact term and explain it.

## Level 1: chat answer

- Fit the length to the question. One concept takes a few short paragraphs without headings, about 250 words at most. An explicit length request is exact: «в пяти предложениях» means five.
- Start with the model in one or two sentences. Then expand it.
- Link cause and effect with «потому что», «поэтому», «если».
- Use lists, tables and headings only when they help the reader compare, follow steps or find a place fast.
- Stop when the model is complete. A second example or a list of nearby facts makes the answer longer, not clearer.

## Check

If you have a shell and the answer is longer than two paragraphs, check the draft:

```bash
python3 <skill-dir>/scripts/ru_score.py --level 80 - <<'EOF'
<draft>
EOF
```

The script threshold is 0.8: the share of sentences with no finding. It has no link to Karpathy's "80%". The script sees structure only. Fix the text for meaning. Do not bend the text to fit the script.

## Final edit pass

Make one pass over all text a human will see:

- **Fidelity.** Each sentence rests on the source or the model. Do not add certainty, causes or judgments for effect.
- **Plain words.** «Использовать», «помогать», «много», «есть». Replace «ключевой», «бесшовный», «надёжный», «уникальный», «экосистема» with a plain word or a number.
- **Mechanism over mood.** Say what the thing does, or give a number.
- **No wrapper.** Do not praise the question. Do not add a closing summary or offer «ещё помочь».
- **Nothing load-bearing lost.** Compare the text with the model. Each condition, caveat, dependency and unknown is either in the text or does not change the reader's conclusion. Restore what the simplification removed.
