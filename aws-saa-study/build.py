"""Build the AWS SAA study guide into dist/index.html (an Artifact page without doctype).

content/*.md format
  @part id | 제목 | 눈썹 | 목차 이름          (course parts use id chNN; number comes from NN)
  intro markdown
  @topic id | 제목 | dom=1,2 | prio=3 | rev=1 | les=Lecture A; Lecture B
  markdown body ([4.1](#topic-id) links get the current number)
  @fig diagram-id                            (extra diagram at this spot; the main one is automatic)
  @practice
  markdown: what each resource does at work, with real-world cases (shown open)
  @easy
  markdown: plain re-explanation, an analogy only where it fits (collapsible)
  @quiz                                      (belongs to the part; Q:/A: pairs)
Diagrams live in dg_*.py (registered by topic id; extras as "topic:name").
"""
import glob
import html
import importlib
import json
import os
import re
import sys

import markdown
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name

import dg
import glossary as GL

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, 'dist')
TITLE = 'AWS SAA 개념 학습서'
DOMAINS = {1: ('보안 아키텍처', 30), 2: ('복원력 있는 아키텍처', 26), 3: ('고성능 아키텍처', 24), 4: ('비용 최적화 아키텍처', 20)}
PRIO = {3: ('r3', '우선순위 높음'), 2: ('r2', '우선순위 보통'), 1: ('r1', '우선순위 낮음'), 0: ('r0', '범위 밖·참고')}

# ---------------------------------------------------------------- parsing


def parse():
    parts = []
    for f in sorted(glob.glob(os.path.join(ROOT, 'content', '*.md'))):
        cur_part = cur_topic = None
        mode = 'intro'
        for raw in open(f, encoding='utf-8').read().split('\n'):
            line = raw.rstrip('\n')
            if line.startswith('@part '):
                pid, title, eyebrow, toc = [x.strip() for x in line[6:].split('|')]
                cur_part = dict(id=pid, title=title, eyebrow=eyebrow, toc=toc, intro=[], topics=[], quiz=[], src=f)
                parts.append(cur_part)
                cur_topic, mode = None, 'intro'
                continue
            if line.startswith('@topic '):
                fields = [x.strip() for x in line[7:].split('|')]
                meta = {}
                for fl in fields[2:]:
                    k, _, v = fl.partition('=')
                    meta[k.strip()] = v.strip()
                cur_topic = dict(id=fields[0], title=fields[1], body=[], easy=[], practice=[], legacy=False, meta=meta, part=cur_part['id'])
                cur_part['topics'].append(cur_topic)
                mode = 'body'
                continue
            if line.strip() in ('@easy', '@analogy'):
                mode = 'easy'
                if line.strip() == '@analogy':
                    cur_topic['legacy'] = True
                continue
            if line.strip() == '@practice':
                mode = 'practice'
                continue
            if line.strip() == '@quiz':
                mode = 'quiz'
                continue
            if mode == 'intro':
                cur_part['intro'].append(line)
            elif mode == 'body':
                cur_topic['body'].append(line)
            elif mode == 'easy':
                cur_topic['easy'].append(line)
            elif mode == 'practice':
                cur_topic['practice'].append(line)
            elif mode == 'quiz':
                cur_part['quiz'].append(line)
    return parts


def parse_quiz(lines):
    items, cur = [], None
    for l in lines:
        if l.startswith('Q:'):
            cur = {'q': [l[2:].strip()], 'a': []}
            items.append(cur)
            tgt = 'q'
        elif l.startswith('A:'):
            cur['a'].append(l[2:].strip())
            tgt = 'a'
        elif cur is not None:
            cur[tgt].append(l)
    return items


# ---------------------------------------------------------------- markdown

CODE_RX = re.compile(r'^(\s*)```(\w*)\s*\n(.*?)\n\1```\s*$', re.S | re.M)
_code_store = {}


def _code_block(m):
    lang = m.group(2) or 'text'
    body = m.group(3)
    try:
        lexer = get_lexer_by_name({'sh': 'bash', 'shell': 'bash'}.get(lang, lang))
        inner = highlight(body, lexer, HtmlFormatter(nowrap=True))
    except Exception:
        inner = html.escape(body)
    label = {'json': 'JSON', 'bash': 'bash', 'sh': 'bash', 'yaml': 'YAML', 'text': '텍스트', 'sql': 'SQL', 'python': 'Python'}.get(lang, lang)
    key = f'@@CODE{len(_code_store)}@@'
    _code_store[key] = (f'<figure class="code"><figcaption><span>{label}</span><button class="copy" type="button">복사</button></figcaption>'
                        f'<pre><code>{inner.rstrip()}</code></pre></figure>')
    return '\n\n' + key + '\n\n'


CALLOUT = {'시험 포인트': 'exam', '주의': 'warn', '참고': 'note', '핵심': 'key', '팁': 'tip', '실제 출제': 'exam', '후기에서': 'tip', '바뀐 점': 'warn'}


def md(text):
    text = CODE_RX.sub(_code_block, text)
    # bold before markdown: python-markdown drops **X)**은 (closing ** after punctuation, before Hangul)
    parts = re.split(r'(`[^`\n]+`)', text)
    for i in range(0, len(parts), 2):
        parts[i] = re.sub(r'\*\*(?=\S)([^*\n]+?)(?<=\S)\*\*', r'<strong>\1</strong>', parts[i])
    text = ''.join(parts)
    h = markdown.markdown(text, extensions=['tables', 'sane_lists'], output_format='html')
    for k, v in list(_code_store.items()):
        h = h.replace(f'<p>{k}</p>', v)

    def bq(m):
        inner = m.group(1)
        mm = re.search(r'<strong>([^<]+)</strong>', inner)
        cls = CALLOUT.get(mm.group(1).strip(), 'note') if mm else 'note'
        return f'<blockquote class="callout {cls}">{inner}</blockquote>'
    h = re.sub(r'<blockquote>(.*?)</blockquote>', bq, h, flags=re.S)

    def tbl(m):
        t = m.group(0)
        heads = re.findall(r'<th[^>]*>(.*?)</th>', t, flags=re.S)
        heads = [re.sub(r'<[^>]+>', '', x).strip() for x in heads]

        def row(rm):
            cells = re.findall(r'<td([^>]*)>(.*?)</td>', rm.group(0), flags=re.S)
            out = []
            for i, (attr, c) in enumerate(cells):
                lab = html.escape(heads[i]) if i < len(heads) else ''
                out.append(f'<td data-label="{lab}"{attr}>{c}</td>')
            return '<tr>\n' + '\n'.join(out) + '\n</tr>'
        body = re.sub(r'<tr>\s*(<td.*?)</tr>', row, t, flags=re.S)
        return f'<div class="table-wrap">{body}</div>'
    h = re.sub(r'<table>.*?</table>', tbl, h, flags=re.S)
    h = re.sub(r'<a href="(https?://[^"]+)">', r'<a href="\1" target="_blank" rel="noopener">', h)
    return h


# ---------------------------------------------------------------- glossary marking

EXCL = {'a', 'code', 'pre', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'figure', 'svg', 'thead', 'th', 'button', 'summary', 'script', 'style', 'figcaption'}


def build_term_rx():
    forms = []
    for e in GL.ENTRIES:
        for f in e['forms']:
            forms.append((f, e['id']))
    forms.sort(key=lambda x: -len(x[0]))
    pats = []
    for f, _ in forms:
        p = re.escape(f)
        if re.match(r'[가-힣]', f):
            pre = r'(?<![가-힣A-Za-z0-9])'
        else:
            pre = r'(?<![A-Za-z0-9_\-/.])'
        post = r'(?![A-Za-z0-9_])' if re.search(r'[A-Za-z0-9]$', f) else ''
        pats.append(pre + p + post)
    rx = re.compile('|'.join(f'({p})' for p in pats))
    return rx, [i for _, i in forms]


TERM_RX, TERM_IDS = None, None


def mark_terms(h, topic_id, part_seen, nomark=False):
    if nomark:
        return h, 0
    seen = set()
    count = 0
    tokens = re.split(r'(<[^>]+>)', h)
    stack = []
    out = []
    for tok in tokens:
        if tok.startswith('<'):
            m = re.match(r'<\s*(/)?\s*([a-zA-Z0-9]+)', tok)
            if m:
                name = m.group(2).lower()
                if m.group(1):
                    if name in stack:
                        while stack and stack[-1] != name:
                            stack.pop()
                        if stack:
                            stack.pop()
                elif not tok.endswith('/>') and name not in ('br', 'img', 'hr', 'input', 'meta', 'link', 'path', 'rect', 'circle', 'ellipse'):
                    cls = re.search(r'class="([^"]*)"', tok)
                    stack.append(name if not (cls and 'term' in cls.group(1).split()) else 'termspan')
            out.append(tok)
            continue
        if not tok or any(s in EXCL or s == 'termspan' for s in stack):
            out.append(tok)
            continue

        def rep(m):
            nonlocal count
            gi = m.lastindex - 1
            gid = TERM_IDS[gi]
            e = GL.BY_ID[gid]
            if gid in seen or (gid in GL.CORE and gid in part_seen) or e['topic'] == topic_id:
                return m.group(0)
            seen.add(gid)
            if gid in GL.CORE:
                part_seen.add(gid)
            count += 1
            return f'<span class="term" role="button" tabindex="0" aria-haspopup="dialog" data-g="{gid}">{m.group(0)}</span>'
        out.append(TERM_RX.sub(rep, tok))
    return ''.join(out), count


# ---------------------------------------------------------------- rendering helpers

def esc(s):
    return html.escape(s, quote=True)


def done_btn(tid):
    return (f'<button class="done" type="button" aria-pressed="false" data-id="{tid}"><span class="done-box" aria-hidden="true"></span>'
            f'<span class="done-text">이해했어요</span></button>')


BRIEF = '<svg class="brief" viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="7" width="18" height="13" rx="2"/><path d="M9 7V5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2M3 13h18"/></svg>'
PENCIL = '<svg class="pencil" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 20l1-5L15.5 4.5a2.1 2.1 0 0 1 3 3L8 18z"/><path d="M13.5 6.5l3 3"/></svg>'


def insert_figure(body_html, fig_html, at):
    if at and at.startswith('end:'):
        key = at[4:]
        m = re.search(r'<h4>[^<]*' + re.escape(key), body_html)
        if m:
            nxt = re.search(r'<h4>|<blockquote class="callout', body_html[m.end():])
            pos = m.end() + nxt.start() if nxt else len(body_html)
            return body_html[:pos] + fig_html + body_html[pos:]
    if at and at != 'top':
        m = re.search(r'<h4>[^<]*' + re.escape(at), body_html)
        if m:
            return body_html[:m.start()] + fig_html + body_html[m.start():]
    if at == 'top':
        return fig_html + body_html
    m = re.search(r'<h4>', body_html)
    if m:
        return body_html[:m.start()] + fig_html + body_html[m.start():]
    m = re.search(r'</p>', body_html)
    if m:
        return body_html[:m.end()] + fig_html + body_html[m.end():]
    return body_html + fig_html


def plain(h):
    t = re.sub(r'<svg.*?</svg>', ' ', h, flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', t)
    t = html.unescape(t)
    return re.sub(r'\s+', ' ', t).strip()


# ---------------------------------------------------------------- main build

def main():
    global TERM_RX, TERM_IDS
    for f in sorted(glob.glob(os.path.join(ROOT, 'dg_*.py'))):
        importlib.import_module(os.path.basename(f)[:-3])
    TERM_RX, TERM_IDS = build_term_rx()
    parts = parse()
    numbering = {}
    for p in parts:
        m = re.match(r'ch(\d+)$', p['id'])
        if m:
            p['no'] = str(int(m.group(1)))
        elif p['id'] == 'appendix':
            p['no'] = 'A'
        else:
            p['no'] = ''
        for i, t in enumerate(p['topics'], 1):
            t['no'] = f"{p['no']}.{i}" if p['no'] else ''
            numbering[t['id']] = t['no']
    titles = {t['id']: t['title'] for p in parts for t in p['topics']}
    all_ids = set(titles)
    warns = []
    used_dg = set()
    total = sum(len(p['topics']) for p in parts)

    # glossary links -> topics
    for e in GL.ENTRIES:
        if e['topic'] and e['topic'] not in all_ids:
            warns.append(f"glossary {e['id']}: unknown topic {e['topic']}")

    def fix_links(h):
        def r(m):
            tid, txt = m.group(1), m.group(2)
            if tid in numbering and re.fullmatch(r'[0-9A-Z]+\.[0-9]+', txt.strip()):
                txt = numbering[tid] or titles[tid]
            if tid not in all_ids and not tid.startswith('part-') and tid not in ('top',):
                warns.append(f'broken link #{tid}')
            return f'<a href="#{tid}">{txt}</a>'
        return re.sub(r'<a href="#([^"]+)">(.*?)</a>', r, h)

    index = []
    toc_html = []
    main_html = []
    term_counts = []
    for p in parts:
        part_seen = set()
        intro = fix_links(md('\n'.join(p['intro']).strip()))
        intro, _ = mark_terms(intro, None, part_seen)
        sec = [f'<section class="part" id="part-{p["id"]}" data-part="{p["id"]}"><header class="part-head">'
               f'<p class="eyebrow">{esc(p["eyebrow"])}</p><h2>{esc(p["title"])}</h2>'
               f'<div class="prose part-intro">{intro}</div></header>']
        toc_items = []
        for t in p['topics']:
            tid = t['id']
            meta = t['meta']
            body = fix_links(md('\n'.join(t['body']).strip()))
            # extra figures placed with @fig
            def figrep(m):
                did = m.group(1)
                if did not in dg.REG:
                    warns.append(f'{tid}: missing diagram {did}')
                    return ''
                used_dg.add(did)
                return dg.REG[did]().figure()
            body = re.sub(r'<p>@fig ([\w:\-]+)</p>', figrep, body)
            if tid in dg.REG:
                D = dg.REG[tid]()
                used_dg.add(tid)
                for w in D.check():
                    warns.append('diagram ' + w)
                body = insert_figure(body, D.figure(), D.at)
            else:
                if tid not in GL.NO_FIG and not tid.startswith(('x-', 'ap-')):
                    warns.append(f'{tid}: concept topic without diagram')
            for extra in [k for k in dg.REG if k.startswith(tid + ':')]:
                if extra not in used_dg:
                    D = dg.REG[extra]()
                    used_dg.add(extra)
                    for w in D.check():
                        warns.append('diagram ' + w)
                    body = insert_figure(body, D.figure(), D.at)
            body, n = mark_terms(body, tid, part_seen, nomark=tid in GL.NO_MARK)
            if tid not in GL.NO_MARK:
                term_counts.append(n)
            # chips
            chips = []
            for d in [x for x in meta.get('dom', '').split(',') if x.strip()]:
                d = int(d)
                name, pct = DOMAINS[d]
                chips.append(f'<a class="dom" href="#x-domains" title="출제 영역 {d}: {name} {pct}%">영역 {d} · {name} {pct}%</a>')
            if 'prio' in meta and meta['prio'] != '':
                pc, pl = PRIO[int(meta['prio'])]
                extra = ' · 후기 언급' if meta.get('rev') == '1' else ''
                chips.append(f'<a class="rev {pc}" href="#x-reviews" title="우선순위 근거는 후기로 본 출제 경향 주제에 있습니다">{pl}{extra}</a>')
            les = [x.strip() for x in meta.get('les', '').split(';') if x.strip()]
            lab_html = ''
            if chips or les:
                lab_html = '<div class="labs">' + ''.join(chips)
                if les:
                    lab_html += '<span class="labs-label">강의</span>' + ''.join(f'<span class="lab">{esc(x)}</span>' for x in les)
                lab_html += '</div>'
            concept = tid not in GL.NO_FIG and not tid.startswith(('x-', 'ap-', 'start-'))
            prac = ''
            if t['practice'] and ''.join(t['practice']).strip():
                prac_body = fix_links(md('\n'.join(t['practice']).strip()))
                prac = (f'<aside class="practice"><p class="practice-h">{BRIEF}실무에서는</p>'
                        f'<div class="practice-body">{prac_body}</div></aside>')
            elif concept:
                warns.append(f'{tid}: no practice cases')
            ana = ''
            if t['easy'] and ''.join(t['easy']).strip():
                ana_body = fix_links(md('\n'.join(t['easy']).strip()))
                ana = (f'<details class="analogy"><summary>{PENCIL}<span class="analogy-label">쉽게 풀어 보기</span>'
                       f'<span class="analogy-hint"></span></summary><div class="analogy-body">{ana_body}</div></details>')
            elif concept:
                warns.append(f'{tid}: no plain explanation')
            if t['legacy']:
                warns.append(f'{tid}: old kid analogy not rewritten yet')
            no = f'<span class="topic-no">{t["no"]}</span>' if t['no'] else ''
            art = (f'<article class="topic" id="{tid}" data-part="{p["id"]}"><header class="topic-head"><h3>{no}{esc(t["title"])}</h3>{done_btn(tid)}</header>'
                   f'{lab_html}<div class="prose">{body}</div>{prac}{ana}'
                   f'<footer class="topic-foot"><span class="topic-foot-hint">다 읽었으면 표시해 두세요</span>{done_btn(tid)}</footer></article>')
            sec.append(art)
            index.append({'id': tid, 'part': p['id'], 't': (t['no'] + ' ' + t['title']).lower(),
                          'x': plain(body + prac + ana).lower()})
            toc_items.append(f'<li><a href="#{tid}" data-id="{tid}"><span class="dot" aria-hidden="true"></span>'
                             f'<span class="nav-no">{t["no"]}</span><span class="nav-title">{esc(t["title"])}</span></a></li>')
        quiz = parse_quiz(p['quiz'])
        if quiz:
            qh = [f'<section class="quiz-block" aria-labelledby="quiz-{p["id"]}"><h3 id="quiz-{p["id"]}">확인 문제 <span class="quiz-count">{len(quiz)}문항</span></h3>'
                  '<p class="quiz-help">먼저 머릿속으로 답한 뒤 눌러서 확인하세요.</p>']
            for i, q in enumerate(quiz, 1):
                qq = fix_links(md('\n'.join(q['q']).strip()))
                aa = fix_links(md('\n'.join(q['a']).strip()))
                qh.append(f'<details class="quiz"><summary><span class="quiz-no">Q{i}</span><span class="quiz-q">{qq}</span></summary>'
                          f'<div class="quiz-a">{aa}</div></details>')
            qh.append('</section>')
            sec.append(''.join(qh))
        sec.append('</section>')
        main_html.append(''.join(sec))
        toc_html.append(f'<div class="toc-part" data-part="{p["id"]}"><a class="toc-part-link" href="#part-{p["id"]}">'
                        f'<span class="toc-part-name">{esc(p["toc"])}</span><span class="toc-count" data-count-for="{p["id"]}">0/{len(p["topics"])}</span></a>'
                        f'<ol>{"".join(toc_items)}</ol></div>')

    # glossary table topic placeholder
    gl_html = GL.render_table(lambda tid: (numbering.get(tid, ''), titles.get(tid, '')))
    joined = ''.join(main_html).replace('<p>@glossary</p>', gl_html)

    gloss_js = {}
    for e in GL.ENTRIES:
        href = f"#{e['topic']}" if e['topic'] else ''
        lab = (numbering.get(e['topic'], '') + ' ' + titles.get(e['topic'], '')).strip() if e['topic'] else ''
        gloss_js[e['id']] = [e['label'], e['en'], e['ko'], md(e['def'])[3:-4] if e['def'].strip() else '', href, lab]

    # unused diagrams
    for k in dg.REG:
        if k not in used_dg and not any(k == t for t in all_ids):
            warns.append(f'diagram {k} registered but not placed')

    # course coverage
    course = json.load(open(os.path.join(ROOT, 'course.json'), encoding='utf-8'))
    covered = set()
    for p in parts:
        for t in p['topics']:
            for x in t['meta'].get('les', '').split(';'):
                if x.strip():
                    covered.add(x.strip())
    all_lect = {}
    for s in course['sections']:
        for l in s['lectures']:
            all_lect[l] = s['no']
    for x in covered:
        if x not in all_lect:
            warns.append(f'lesson name not in course: "{x}"')
    built_secs = {int(p['id'][2:]) for p in parts if re.match(r'ch\d+$', p['id'])}
    missing = [f'{all_lect[l]}: {l}' for l in all_lect if all_lect[l] in built_secs and l not in covered]

    tpl_css = open(os.path.join(ROOT, 'tpl', 'base.css'), encoding='utf-8').read()
    extra_css = open(os.path.join(ROOT, 'tpl', 'extra.css'), encoding='utf-8').read()
    app = open(os.path.join(ROOT, 'tpl', 'app.js'), encoding='utf-8').read()
    cfg = {"key": "aws-saa-study:done:v1", "doneOn": "이해 완료", "doneOff": "이해했어요", "toggleSel": "details.analogy",
           "longOpen": "풀이 모두 펼치기", "longClose": "풀이 모두 접기", "shortOpen": "풀이 펼치기", "shortClose": "풀이 접기"}
    app = (app.replace('__INDEX__', json.dumps(index, ensure_ascii=False))
              .replace('__CFG__', json.dumps(cfg, ensure_ascii=False))
              .replace('__TOTAL__', str(total))
              .replace('__GLOSS__', json.dumps(gloss_js, ensure_ascii=False)))
    hero = open(os.path.join(ROOT, 'tpl', 'hero.html'), encoding='utf-8').read()
    termpop = open(os.path.join(ROOT, 'tpl', 'termpop.html'), encoding='utf-8').read()
    page = f'''<title>{TITLE}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans+KR:wght@400;500;600;700&display=swap">
<style>
{tpl_css}
{extra_css}
</style>

<header class="bar">
  <div class="bar-inner">
    <button class="toc-btn" type="button" id="toc-btn" aria-controls="rail" aria-expanded="false">목차</button>
    <a class="brand" href="#top">{TITLE}<small>SAA-C03</small></a>
    <label class="search" for="q">
      <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>
      <input id="q" type="search" placeholder="개념 검색 (예: NAT, 스팟, Aurora, 수명 주기)" autocomplete="off" aria-label="개념 검색">
    </label>
    <div class="progress" title="이해했어요로 표시한 주제 수">
      <span id="prog-text">0 / {total}</span><span class="meter" aria-hidden="true"><span id="prog-bar"></span></span>
    </div>
    <button class="ghost-btn" type="button" id="toggle-analogies" aria-pressed="false"><span class="t-long">풀이 모두 펼치기</span><span class="t-short">풀이 펼치기</span></button>
  </div>
</header>
<div class="scrim" id="scrim"></div>

<div class="layout" id="top">
  <aside class="rail" id="rail" aria-label="목차">
    <nav id="toc">{"".join(toc_html)}</nav>
    <p class="rail-foot">체크한 진도는 이 브라우저에만 저장됩니다.</p>
  </aside>

  <main class="main" id="main">
    <div class="search-status" role="status"><span id="search-msg"></span><button type="button" id="search-clear">검색 지우기</button></div>
    <p class="empty">검색 결과가 없습니다. 서비스 이름(예: <code>sqs</code>, <code>efs</code>)이나 다른 단어로 검색해 보세요.</p>
{hero}
{joined}
    <footer class="page-foot">
      <p>시험 정보 출처: AWS Certification 시험 안내와 SAA-C03 시험 가이드(2026-10-19 확인). 강의 목차: Stephane Maarek, Ultimate AWS Certified Solutions Architect Associate (Udemy, 2026-10-19 확인). 서비스 사실은 각 주제의 AWS 공식 문서 링크로 확인했습니다. AWS는 서비스를 자주 바꾸므로 시험 직전에 공식 문서를 한 번 더 보세요.</p>
    </footer>
  </main>
</div>
{termpop}
<script>
{app}
</script>
'''
    os.makedirs(DIST, exist_ok=True)
    open(os.path.join(DIST, 'index.html'), 'w', encoding='utf-8').write(page)
    # gallery for svg text measurement
    gal = ['<title>그림 갤러리</title><style>' + tpl_css + extra_css + '</style><main class="main" style="max-width:none">']
    for k in sorted(dg.REG):
        D = dg.REG[k]()
        gal.append(f'<section><h3>{esc(k)}</h3>{D.figure()}</section>')
    gal.append('</main>')
    open(os.path.join(DIST, 'gallery.html'), 'w', encoding='utf-8').write(''.join(gal))

    ids = re.findall(r'(?<![\w-])id="([^"]+)"', page)
    dups = sorted({i for i in ids if ids.count(i) > 1})
    for d in dups:
        warns.append(f'duplicate id {d}')
    term_counts.sort()
    med = term_counts[len(term_counts) // 2] if term_counts else 0
    print(f'topics {total}, diagrams {len(used_dg)}, page {len(page) / 1024:.0f} KB, term popovers median {med} max {max(term_counts) if term_counts else 0}')
    print(f'course lessons in built sections not covered: {len(missing)}')
    for x in missing:
        print('  missing lesson', x)
    print(f'warnings: {len(warns)}')
    for w in warns:
        print('  ' + w)


if __name__ == '__main__':
    main()
