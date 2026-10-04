import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/m3m-explain'
FIND_SKILL = SKILL / 'scripts/find_skill.py'


def load(name):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, SKILL / f'scripts/{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_skill(base: Path, rel: str) -> Path:
    folder = base / rel
    folder.mkdir(parents=True)
    (folder / 'SKILL.md').write_text('---\nname: x\n---\n', encoding='utf-8')
    return folder


class FindSkillTest(unittest.TestCase):
    def setUp(self):
        self.fs = load('find_skill')
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_finds_in_claude_skills(self):
        folder = make_skill(self.home, '.claude/skills/faceless-explainer')
        self.assertEqual(self.fs.find_skill('faceless-explainer', self.home), folder)

    def test_finds_in_agents_skills(self):
        folder = make_skill(self.home, '.agents/skills/faceless-explainer')
        self.assertEqual(self.fs.find_skill('faceless-explainer', self.home), folder)

    def test_finds_in_plugin_cache(self):
        folder = make_skill(self.home, '.claude/plugins/cache/hf/hyperframes/1.0/skills/faceless-explainer')
        self.assertEqual(self.fs.find_skill('faceless-explainer', self.home), folder)

    def test_requires_skill_md(self):
        (self.home / '.claude/skills/faceless-explainer').mkdir(parents=True)
        self.assertIsNone(self.fs.find_skill('faceless-explainer', self.home))

    def test_cli_not_found_exit_1(self):
        result = subprocess.run([sys.executable, str(FIND_SKILL), 'nope'], capture_output=True, text=True,
                                env={**os.environ, 'HOME': str(self.home)})
        self.assertEqual(result.returncode, 1)
        self.assertIn('not found: nope', result.stdout + result.stderr)


INSTALL = ROOT / 'install.sh'


class InstallTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name) / 'home dir'
        self.home.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def run_install(self, *args, script=INSTALL, extra_env=None):
        env = {**os.environ, 'HOME': str(self.home), **(extra_env or {})}
        return subprocess.run(['bash', str(script), *args], capture_output=True, text=True, env=env, timeout=120)

    def installed(self, rel):
        return (self.home / rel / 'm3m-explain' / 'SKILL.md').is_file()

    def test_default_creates_claude_dir(self):
        result = self.run_install()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(self.installed('.claude/skills'))

    def test_installs_into_existing_dirs(self):
        (self.home / '.claude/skills').mkdir(parents=True)
        (self.home / '.agents/skills').mkdir(parents=True)
        self.assertEqual(self.run_install().returncode, 0)
        self.assertTrue(self.installed('.claude/skills'))
        self.assertTrue(self.installed('.agents/skills'))

    def test_target_agents_only(self):
        self.assertEqual(self.run_install('--target', 'agents').returncode, 0)
        self.assertTrue(self.installed('.agents/skills'))
        self.assertFalse((self.home / '.claude/skills/m3m-explain').exists())

    def test_reinstall_replaces_without_nesting(self):
        self.run_install()
        (self.home / '.claude/skills/m3m-explain/stale.txt').write_text('old')
        self.assertEqual(self.run_install().returncode, 0)
        target = self.home / '.claude/skills/m3m-explain'
        self.assertFalse((target / 'stale.txt').exists())
        self.assertFalse((target / 'm3m-explain').exists())
        self.assertTrue((target / 'SKILL.md').is_file())

    def test_home_with_space(self):
        self.assertIn(' ', str(self.home))
        self.assertEqual(self.run_install().returncode, 0)
        self.assertTrue(self.installed('.claude/skills'))

    def test_dry_run_changes_nothing(self):
        result = self.run_install('--with-video', '--dry-run')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('npx hyperframes skills update', result.stdout)
        self.assertFalse((self.home / '.claude').exists())

    def test_uninstall_removes(self):
        self.run_install('--target', 'all')
        result = self.run_install('--uninstall')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.home / '.claude/skills/m3m-explain').exists())
        self.assertFalse((self.home / '.agents/skills/m3m-explain').exists())

    def test_archive_mode(self):
        import shutil
        import tarfile
        work = Path(self.tmp.name)
        archive = work / 'repo.tar.gz'
        with tarfile.open(archive, 'w:gz') as tar:
            tar.add(SKILL, arcname='m3m-explain-main/skills/m3m-explain')
        lone = work / 'lone'
        lone.mkdir()
        shutil.copy(INSTALL, lone / 'install.sh')
        result = self.run_install(script=lone / 'install.sh', extra_env={'M3M_ARCHIVE': str(archive)})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(self.installed('.claude/skills'))


RU_SCORE = SKILL / 'scripts/ru_score.py'


def run_ru_score(text: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(RU_SCORE), *args],
        input=text,
        capture_output=True,
        text=True,
    )


class RuScoreTest(unittest.TestCase):
    def test_self_test_passes(self):
        result = run_ru_score('', '--self-test')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_clean_text_scores_one(self):
        result = run_ru_score('Скрипт изменил конфиг. Проверьте лог.\n', '--json', '-')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['score'], 1.0)

    def test_kantselyarit_fails(self):
        text = 'Данный конфиг был изменён в рамках задачи; необходимо осуществить проверку.\n'
        result = run_ru_score(text, '--json', '-')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertLess(json.loads(result.stdout)['score'], 0.8)


def load_check_page():
    import importlib.util
    spec = importlib.util.spec_from_file_location('check_page', SKILL / 'scripts/check_page.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CLEAN = '<!doctype html><html lang="ru"><head><meta charset="utf-8"></head><body><p>Привет</p></body></html>'


def with_body(fragment: str) -> str:
    return CLEAN.replace('<p>Привет</p>', fragment)


class CheckPageTest(unittest.TestCase):
    def setUp(self):
        self.cp = load_check_page()

    def issues(self, html: str, **kwargs):
        return self.cp.static_issues(html, len(html.encode()), **kwargs)

    def test_clean_page_passes(self):
        self.assertEqual(self.issues(CLEAN), [])

    def test_external_src_flagged(self):
        self.assertEqual(len(self.issues(with_body('<img src="https://x/a.png">'))), 1)

    def test_css_url_flagged(self):
        self.assertEqual(len(self.issues(with_body('<div style="background:url(http://x/a.png)"></div>'))), 1)

    def test_link_stylesheet_flagged(self):
        self.assertEqual(len(self.issues(with_body('<link rel="stylesheet" href="https://cdn/x.css">'))), 1)

    def test_anchor_href_allowed(self):
        self.assertEqual(self.issues(with_body('<a href="https://example.com">источник</a>')), [])

    def test_fill_marker_flagged(self):
        self.assertEqual(len(self.issues(with_body('<p>FILL</p>'))), 1)

    def test_missing_charset_flagged(self):
        self.assertEqual(len(self.issues(CLEAN.replace('<meta charset="utf-8">', ''))), 1)

    def test_size_limit(self):
        self.assertEqual(len(self.cp.static_issues(CLEAN, 201 * 1024, max_kb=200)), 1)

    def test_find_chrome_none(self):
        self.assertIsNone(self.cp.find_chrome(['/nonexistent/chrome']))

    def test_find_chrome_sees_hyperframes_headless_shell(self):
        import os, tempfile
        with tempfile.TemporaryDirectory() as home:
            shell = Path(home) / '.cache/hyperframes/chrome/chrome-headless-shell/mac/chrome-headless-shell'
            shell.parent.mkdir(parents=True)
            shell.write_text('#!/bin/sh\n')
            os.chmod(shell, 0o755)
            self.assertIn(str(shell), self.cp._default_candidates(Path(home)))

    def test_narrow_overflow_detects_long_url(self):
        import tempfile
        chrome = self.cp.find_chrome()
        if not chrome:
            self.skipTest('Chrome не найден')
        long_url = 'https://accounts.google.com/o/oauth2/v2/auth?client_id=' + 'x' * 120
        with tempfile.TemporaryDirectory() as d:
            bad = Path(d) / 'bad.html'
            bad.write_text(with_body(f'<p>{long_url}</p>'), encoding='utf-8')
            self.assertTrue(self.cp.narrow_overflow(bad, chrome))
            good = Path(d) / 'good.html'
            good.write_text(CLEAN, encoding='utf-8')
            self.assertFalse(self.cp.narrow_overflow(good, chrome))

    def test_narrow_wrapper_uses_390_iframe(self):
        html = self.cp.narrow_wrapper('file:///tmp/page.html')
        self.assertIn('<iframe src="file:///tmp/page.html"', html)
        self.assertIn('width: 390px', html)
        self.assertIn('background: #808080', html)


TEMPLATE = SKILL / 'assets/page.html'


class TemplateTest(unittest.TestCase):
    def test_template_only_fill_issues(self):
        html = TEMPLATE.read_text(encoding='utf-8')
        issues = load_check_page().static_issues(html, len(html.encode()))
        self.assertTrue(issues)
        self.assertTrue(all('FILL' in issue for issue in issues), issues)

    def test_template_contract(self):
        html = TEMPLATE.read_text(encoding='utf-8')
        for needle in ('lang="ru"', 'prefers-reduced-motion', 'prefers-color-scheme',
                       '#step=', 'data-slider', 'data-path', 'max-width: 100%'):
            self.assertIn(needle, html)

    def test_template_size(self):
        self.assertLessEqual(TEMPLATE.stat().st_size, 30 * 1024)

    def test_template_styles_links_for_both_themes(self):
        self.assertIn('a { color: var(--accent); }', TEMPLATE.read_text(encoding='utf-8'))

    def test_template_wraps_long_words(self):
        self.assertIn('overflow-wrap: anywhere', TEMPLATE.read_text(encoding='utf-8'))

    def test_slider_handler_defined_later_runs_on_load(self):
        import tempfile
        chrome = load_check_page().find_chrome()
        if not chrome:
            self.skipTest('Chrome не найден')
        html = TEMPLATE.read_text(encoding='utf-8').replace(
            '</body>',
            '<script>window.onSlider = function (v) { document.body.dataset.slid = String(v); };</script></body>')
        with tempfile.TemporaryDirectory() as d:
            page = Path(d) / 'p.html'
            page.write_text(html, encoding='utf-8')
            dom = subprocess.run(
                [chrome, '--headless=new', '--disable-gpu', '--virtual-time-budget=2000', '--dump-dom', page.as_uri()],
                capture_output=True, text=True, timeout=60).stdout
        self.assertIn('data-slid="50"', dom)

    def test_hidden_step_fades_instead_of_vanishing(self):
        import tempfile
        chrome = load_check_page().find_chrome()
        if not chrome:
            self.skipTest('Chrome не найден')
        probe = ("<script>window.addEventListener('load', function () {"
                 "var g = document.querySelector('.step[hidden]'); var cs = getComputedStyle(g);"
                 "document.body.dataset.disp = cs.display; document.body.dataset.op = cs.opacity; });</script></body>")
        html = TEMPLATE.read_text(encoding='utf-8').replace('</body>', probe)
        with tempfile.TemporaryDirectory() as d:
            page = Path(d) / 'p.html'
            page.write_text(html, encoding='utf-8')
            dom = subprocess.run(
                [chrome, '--headless=new', '--disable-gpu', '--virtual-time-budget=2000', '--dump-dom', page.as_uri()],
                capture_output=True, text=True, timeout=60).stdout
        self.assertIn('data-op="0"', dom)
        self.assertNotIn('data-disp="none"', dom)

    def test_stepper_controls_before_notes(self):
        html = TEMPLATE.read_text(encoding='utf-8')
        stepper = html[html.index('class="stepper"'):html.index('</figure>')]
        self.assertLess(stepper.index('class="controls"'), stepper.index('data-step-note="1"'))

    def test_template_mobile_figure_scroll(self):
        html = TEMPLATE.read_text(encoding='utf-8')
        self.assertIn('overflow-x: auto', html)
        self.assertIn('min-width: 560px', html)

    def test_stepper_hash_hides_later_steps(self):
        chrome = load_check_page().find_chrome()
        if not chrome:
            self.skipTest('Chrome не найден')
        dom = subprocess.run(
            [chrome, '--headless=new', '--disable-gpu', '--virtual-time-budget=2000', '--dump-dom',
             TEMPLATE.resolve().as_uri() + '#step=1'],
            capture_output=True, text=True, timeout=60,
        ).stdout
        self.assertRegex(dom, r'<g class="step" data-step="2" hidden')
        self.assertRegex(dom, r'<g class="step" data-step="3" hidden')
        self.assertNotRegex(dom, r'<g class="step" data-step="1" hidden')


SKILL_MD = SKILL / 'SKILL.md'


def split_skill_md():
    text = SKILL_MD.read_text(encoding='utf-8')
    _, front, body = text.split('---', 2)
    fields = {}
    for line in front.strip().splitlines():
        key, _, value = line.partition(':')
        fields[key.strip()] = value.strip().strip('"')
    return fields, body


def load_sfx_offsets():
    import importlib.util
    spec = importlib.util.spec_from_file_location('sfx_offsets', SKILL / 'scripts/sfx_offsets.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


STORYBOARD = """---
music: none
---

## Frame 1 — Тезис

- duration: 5s
- sfx: pop, chime
- sfx_at: 0.5, 3

Текст.

## Frame 2 — Причина

- duration: 4s
- sfx: whoosh

Текст.
"""


def meta_with(*frames):
    return {'bgm': None, 'voices': [], 'sfx': [
        {'frame': f, 'file': f'assets/sfx/{i}.mp3', 'offset_s': 0, 'duration_s': 0.5, 'volume': 0.35}
        for i, f in enumerate(frames)]}


class SfxOffsetsTest(unittest.TestCase):
    def setUp(self):
        self.so = load_sfx_offsets()

    def test_offsets_applied_in_order(self):
        meta = self.so.apply_offsets(STORYBOARD, meta_with(1, 1, 2))
        self.assertEqual([c['offset_s'] for c in meta['sfx']], [0.5, 3.0, 0])

    def test_empty_field_before_sfx_at_keeps_offsets(self):
        board = STORYBOARD.replace('- sfx_at: 0.5, 3', '- voiceover:\n- sfx_at: 0.5, 3')
        meta = self.so.apply_offsets(board, meta_with(1, 1, 2))
        self.assertEqual([c['offset_s'] for c in meta['sfx']], [0.5, 3.0, 0])

    def test_offset_beyond_frame_duration_rejected(self):
        with self.assertRaises(ValueError):
            self.so.apply_offsets(STORYBOARD.replace('sfx_at: 0.5, 3', 'sfx_at: 0.5, 6'), meta_with(1, 1, 2))

    def test_repeated_sound_gets_a_cue_per_mention(self):
        board = STORYBOARD.replace('- sfx: pop, chime\n- sfx_at: 0.5, 3', '- sfx: pop, pop, chime\n- sfx_at: 0.5, 1, 3')
        meta = {'bgm': None, 'voices': [], 'sfx': [
            {'frame': 1, 'file': 'assets/sfx/pop.mp3', 'offset_s': 0, 'duration_s': 0.7, 'volume': 0.35},
            {'frame': 1, 'file': 'assets/sfx/chime.mp3', 'offset_s': 0, 'duration_s': 2.5, 'volume': 0.35},
            {'frame': 2, 'file': 'assets/sfx/whoosh.mp3', 'offset_s': 0, 'duration_s': 0.6, 'volume': 0.35}]}
        meta = self.so.apply_offsets(board, meta)
        self.assertEqual([(c['file'].split('/')[-1], c['offset_s']) for c in meta['sfx']],
                         [('pop.mp3', 0.5), ('pop.mp3', 1.0), ('chime.mp3', 3.0), ('whoosh.mp3', 0)])

    def test_more_offsets_than_cues_rejected(self):
        with self.assertRaises(ValueError):
            self.so.apply_offsets(STORYBOARD, meta_with(1, 2))


class VideoDocTest(unittest.TestCase):
    def test_env_check_reports_each_failure_and_never_downloads(self):
        text = (SKILL / 'references/video.md').read_text(encoding='utf-8')
        block = text.split('## 2.', 1)[1].split('```bash', 1)[1].split('```', 1)[0]
        lines = [l for l in block.strip().splitlines() if l.strip()]
        self.assertGreaterEqual(len(lines), 5)
        for line in lines:
            self.assertIn('|| echo', line)
        self.assertNotIn('browser ensure', text)


class SkillDocsTest(unittest.TestCase):
    def test_frontmatter(self):
        fields, _ = split_skill_md()
        self.assertEqual(fields['name'], 'm3m-explain')
        self.assertNotIn('machine', fields)
        self.assertIn('объясни', fields['description'])
        self.assertTrue(fields['description'].startswith('Use when'))
        self.assertLessEqual(len(fields['description']), 500)

    def test_body_word_budget(self):
        _, body = split_skill_md()
        self.assertLessEqual(len(body.split()), 600)

    def test_references_exist(self):
        _, body = split_skill_md()
        import re
        paths = set(re.findall(r'`((?:references|scripts|assets)/[\w./-]+)`', body))
        self.assertTrue(paths)
        for rel in paths:
            self.assertTrue((SKILL / rel).exists(), rel)




class PublicDocsTest(unittest.TestCase):
    def test_text_ru_exists(self):
        self.assertTrue((SKILL / 'references/text-ru.md').is_file())

    def test_ste_score_runs(self):
        result = subprocess.run([sys.executable, str(SKILL / 'scripts/ste_score.py'), '--json', '-'],
                                input='Open the file. Read the log.\n', capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_no_owner_paths(self):
        for path in SKILL.rglob('*.md'):
            text = path.read_text(encoding='utf-8')
            for needle in ('~/.agents/skills/explain', '/library', 'HYPERFRAMES_SKIP_SKILLS'):
                self.assertNotIn(needle, text, f'{needle} in {path}')


PERSONAL = ('/Users/', '/home/', 'damnlav', 'Node7', 'spark-eadb', 'memorion', 'меморион', 'm3morion', '192.168.')


class LeakTest(unittest.TestCase):
    def test_no_personal_data(self):
        # what git would publish: tracked plus untracked files that .gitignore does not exclude
        listed = subprocess.run(['git', 'ls-files', '--cached', '--others', '--exclude-standard'],
                                cwd=ROOT, capture_output=True, text=True, check=True).stdout.splitlines()
        self.assertTrue(listed)
        for path in (ROOT / rel for rel in listed):
            if not path.is_file() or path.suffix in ('.mp4', '.jpg', '.png', '.woff2'):
                continue
            if path.name == 'test_m3m_explain.py':
                continue
            text = path.read_text(encoding='utf-8', errors='ignore')
            for needle in PERSONAL:
                self.assertNotIn(needle.lower(), text.lower(), f'{needle} in {path}')


if __name__ == '__main__':
    unittest.main()
