# Text: plain-English rules and level 1

## Where the rules come from

Karpathy asks for explanations in ASD-STE100 and sometimes softens the request: "80% of the way to ASD-STE100", because "the spec is quite stringent". He says nothing more about the 80%.

ASD-STE100 is a controlled language for English. This skill borrows its structural rules (2-5, 9 and 10 below) and adds the information-style rule "answer first" (1). The rule set and the name plain-en-80 follow the legible skill (oshnilia/claude-plugins). This is a house style, not compliance with the standard. Never call a text "ASD-STE100 compliant".

Soften the way Karpathy does: keep structural rules strict, keep the vocabulary softer. Terms, a rare passive and one or two comparisons are fine. This reading comes from output-form-ladder. Karpathy does not state it.

For Russian text, use `text-ru.md`.

## Rules (plain-en-80)

They apply to everything a human reads: chat answers, diagram labels, page text, on-screen text in videos.

1. Answer first. Give the reasons after.
2. A descriptive sentence has at most 25 words. A procedural sentence has at most 20 words.
3. One idea or one action in each sentence.
4. Put the condition before the action: "If the test fails, read the log."
5. Use the active voice. Name the actor: "The script changed the config."
6. Use simple words with one meaning. Say "use", not "utilize". Say "start", not "commence".
7. One term has one meaning in the whole text. Do not rotate synonyms for one thing. Explain a term at first use. Leave code and technical names as they are.
8. Use a verb, not a noun that hides the action: "check the file", not "perform a check of the file".
9. No semicolons.
10. A paragraph has one topic and at most 6 sentences.

Honesty comes before simplicity:

- Mark inference and unknowns in the same sentence: "probably", "the source does not say". Say what would settle the question.
- Write your own design as a recommendation with a condition: "If tasks must resume, the event log should be the source of truth."
- Mark an invented example as an illustration.
- Do not swap a technical term for a simple but wrong word. Give the exact term and explain it.

## Level 1: chat answer

- Fit the length to the question. One concept takes a few short paragraphs without headings, about 250 words at most. An explicit length request is exact: "in five sentences" means five.
- Start with the model in one or two sentences. Then expand it.
- Link cause and effect with "because", "so", "if".
- Use lists, tables and headings only when they help the reader compare, follow steps or find a place fast.
- Stop when the model is complete. A second example or a list of nearby facts makes the answer longer, not clearer.

## Check

If you have a shell and the answer is longer than two paragraphs, check the draft:

```bash
python3 <skill-dir>/scripts/ste_score.py --level 80 - <<'EOF'
<draft>
EOF
```

The script threshold is 0.8: the share of sentences with no finding. It has no link to Karpathy's "80%". The script sees structure only. Fix the text for meaning. Do not bend the text to fit the script.

## Final edit pass

Make one pass over all text a human will see:

- **Fidelity.** Each sentence rests on the source or the model. Do not add certainty, causes or judgments for effect.
- **Plain words.** "Use", "help", "many", "have". Replace "key", "seamless", "robust", "unique", "ecosystem" with a plain word or a number.
- **Mechanism over mood.** Say what the thing does, or give a number.
- **No wrapper.** Do not praise the question. Do not add a closing summary or offer "more help".
- **Nothing load-bearing lost.** Compare the text with the model. Each condition, caveat, dependency and unknown is either in the text or does not change the reader's conclusion. Restore what the simplification removed.
