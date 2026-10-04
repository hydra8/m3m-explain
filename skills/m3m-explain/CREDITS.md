# Credits

The skill is built from ideas and rules in these MIT repositories. The rule texts are retold and translated. Only `scripts/ru_score.py` and `scripts/ste_score.py` are copied verbatim.

| Repository | What was taken |
|---|---|
| [v60samurai/claritymaxx](https://github.com/v60samurai/claritymaxx) | the model before the wording, the table of difficulty shapes, calibration, the two mistakes, "reasons that do not decide the step" |
| [lklbar666/output-form-ladder](https://github.com/lklbar666/output-form-ladder) | stop rules, "change the medium, not the wording", one level at a time, the meaning of "80%" |
| [oshnilia/claude-plugins](https://github.com/oshnilia/claude-plugins) (`legible/plain-russian`) | the plain-ru-80 rules, `scripts/ru_score.py` (copy, unchanged) |
| [oshnilia/claude-plugins](https://github.com/oshnilia/claude-plugins) (`legible/plain-english`) | the plain-en-80 rules, `scripts/ste_score.py` (copy, unchanged) |
| [elliewlh2094/explain-as-webpage](https://github.com/elliewlh2094/explain-as-webpage) | interaction steps inside HTML, the "showy" red flag, grep checks and screenshots at 1280/390 |
| [ohernandezdev/karpathy-output](https://github.com/ohernandezdev/karpathy-output) | announcing the level in one line; never claim a video without a real render |
| [mblode/agent-skills](https://github.com/mblode/agent-skills) (`eli5`) | expensive levels only after a question |

The ladder idea comes from Andrej Karpathy's post, https://x.com/karpathy/status/2105819303471976479.

## License of `scripts/ru_score.py` and `scripts/ste_score.py`

Both scripts are copied unchanged from oshnilia/claude-plugins and share this license.

```
MIT License

Copyright (c) 2026 Ilia

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## PT Sans font

`assets/fonts/PTSans-*.woff2` is PT Sans (ParaType), the cyrillic and latin sets from Google Fonts. License: SIL Open Font License 1.1, text in `assets/fonts/OFL.txt`. The files are unchanged. In CSS the font is loaded as `Explain Sans`.
