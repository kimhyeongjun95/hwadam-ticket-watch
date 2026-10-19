"""Diagram engine: boxes, groups and orthogonal arrows drawn as inline SVG.

Every diagram is drawn twice from one layout: the formal version (AWS names) and the
analogy version (kid labels k=/ksub=/kicon=). Colors come from CSS classes only, so the
same SVG works in light and dark themes. check() reports text that does not fit, overlaps,
lines running through labels and anything outside the viewBox; the build prints these.
"""
import html
from icons import ICONS

REG = {}          # diagram id -> builder function


def reg(did):
    def deco(fn):
        if did in REG:
            raise ValueError("duplicate diagram id " + did)
        REG[did] = fn
        return fn
    return deco


def esc(s):
    return html.escape(s, quote=True)


def char_w(ch):
    o = ord(ch)
    if (0xAC00 <= o <= 0xD7A3 or 0x3130 <= o <= 0x318F or 0x4E00 <= o <= 0x9FFF
            or 0x2460 <= o <= 0x24FF or 0x3000 <= o <= 0x303F or 0xFF00 <= o <= 0xFFEF
            or 0x2190 <= o <= 0x21FF or 0x2190 <= o <= 0x2BFF):
        return 1.0
    if ch == ' ':
        return 0.28
    if ch in "il.,:;|!'`":
        return 0.3
    if ch in 'fjtrI()[]{}/-':
        return 0.4
    if ch in 'mwMW%@':
        return 0.88
    if ch in '·':
        return 0.3
    if ch.isupper():
        return 0.68
    if ch.isdigit():
        return 0.6
    if ch.islower():
        return 0.56
    return 0.62


def text_w(s, size, bold=False):
    return sum(char_w(c) for c in s) * size * (1.05 if bold else 1.0)


LBL, SUB, ELBL, GLBL = 14, 12, 12, 12.5


class Node:
    def __init__(self, key, x, y, w, h, lbl, sub=None, icon=None, t='plain', k=None, ksub=None,
                 kicon=None, lay=None):
        self.key, self.x, self.y, self.w, self.h = key, x, y, w, h
        self.lbl, self.sub, self.icon, self.t = lbl, sub, icon, t
        self.k, self.ksub, self.kicon, self.lay = k, ksub, kicon, lay

    @property
    def cx(self):
        return self.x + self.w / 2

    @property
    def cy(self):
        return self.y + self.h / 2

    def rect(self):
        return (self.x, self.y, self.w, self.h)

    def texts(self, kid):
        if kid and self.k is not None:
            lbl = self.k
            sub = self.ksub
        else:
            lbl = self.lbl
            sub = self.sub
        icon = (self.kicon or self.icon) if kid else self.icon
        return lbl, sub, icon


class Edge:
    def __init__(self, a, b, lbl=None, k=None, t='n', dash=False, both=False, sa=None, sb=None,
                 via=None, lp=None, lo=0.5, path=None):
        self.a, self.b, self.lbl, self.k, self.t = a, b, lbl, k, t
        self.dash, self.both, self.sa, self.sb = dash, both, sa, sb
        self.via, self.lp, self.lo, self.path = via or [], lp, lo, path


def _anchor(n, side):
    if isinstance(side, tuple):
        side, f = side
    else:
        f = 0.5
    if side == 'r':
        return (n.x + n.w, n.y + n.h * f)
    if side == 'l':
        return (n.x, n.y + n.h * f)
    if side == 't':
        return (n.x + n.w * f, n.y)
    if side == 'b':
        return (n.x + n.w * f, n.y + n.h)
    raise ValueError(side)


def _sidename(s):
    return s[0] if isinstance(s, tuple) else s


def route(e, A, B):
    """Return the polyline (list of points) for edge e between nodes A and B."""
    if e.via:
        sa = e.sa or 'r'
        sb = e.sb or 'l'
        return [_anchor(A, sa)] + list(e.via) + [_anchor(B, sb)]
    if e.sa or e.sb:
        sa = e.sa or _auto_side(A, B)
        sb = e.sb or _opposite(_sidename(sa))
        p, q = _anchor(A, sa), _anchor(B, sb)
        ha, hb = _sidename(sa) in 'rl', _sidename(sb) in 'rl'
        if ha and hb:
            if abs(p[1] - q[1]) < 0.5:
                return [p, q]
            mx = (p[0] + q[0]) / 2
            return [p, (mx, p[1]), (mx, q[1]), q]
        if not ha and not hb:
            if abs(p[0] - q[0]) < 0.5:
                return [p, q]
            my = (p[1] + q[1]) / 2
            return [p, (p[0], my), (q[0], my), q]
        if ha and not hb:
            return [p, (q[0], p[1]), q]
        return [p, (p[0], q[1]), q]
    ax0, ax1, bx0, bx1 = A.x, A.x + A.w, B.x, B.x + B.w
    ay0, ay1, by0, by1 = A.y, A.y + A.h, B.y, B.y + B.h
    hov = min(ax1, bx1) - max(ax0, bx0)
    vov = min(ay1, by1) - max(ay0, by0)
    if hov >= 16 and (by0 >= ay1 or ay0 >= by1):
        x = (max(ax0, bx0) + min(ax1, bx1)) / 2
        return [(x, ay1), (x, by0)] if by0 >= ay1 else [(x, ay0), (x, by1)]
    if vov >= 16 and (bx0 >= ax1 or ax0 >= bx1):
        y = (max(ay0, by0) + min(ay1, by1)) / 2
        return [(ax1, y), (bx0, y)] if bx0 >= ax1 else [(ax0, y), (bx1, y)]
    dx, dy = B.cx - A.cx, B.cy - A.cy
    if abs(dx) >= abs(dy):
        p = (ax1, A.cy) if dx > 0 else (ax0, A.cy)
        q = (bx0, B.cy) if dx > 0 else (bx1, B.cy)
        mx = (p[0] + q[0]) / 2
        return [p, (mx, p[1]), (mx, q[1]), q]
    p = (A.cx, ay1) if dy > 0 else (A.cx, ay0)
    q = (B.cx, by0) if dy > 0 else (B.cx, by1)
    my = (p[1] + q[1]) / 2
    return [p, (p[0], my), (q[0], my), q]


def _auto_side(A, B):
    dx, dy = B.cx - A.cx, B.cy - A.cy
    if abs(dx) >= abs(dy):
        return 'r' if dx > 0 else 'l'
    return 'b' if dy > 0 else 't'


def _opposite(s):
    return {'r': 'l', 'l': 'r', 't': 'b', 'b': 't'}[s]


def _seg_hits_rect(p, q, r, pad=0.0):
    """Liang-Barsky: does segment p-q pass through rect r=(x,y,w,h) shrunk by pad?"""
    x0, y0, x1, y1 = r[0] + pad, r[1] + pad, r[0] + r[2] - pad, r[1] + r[3] - pad
    if x1 <= x0 or y1 <= y0:
        return False
    dx, dy = q[0] - p[0], q[1] - p[1]
    t0, t1 = 0.0, 1.0
    for pp, qq in ((-dx, p[0] - x0), (dx, x1 - p[0]), (-dy, p[1] - y0), (dy, y1 - p[1])):
        if pp == 0:
            if qq < 0:
                return False
        else:
            t = qq / pp
            if pp < 0:
                t0 = max(t0, t)
            else:
                t1 = min(t1, t)
            if t0 > t1:
                return False
    return t1 - t0 > 1e-6


def _ov(a, b, pad=0.0):
    return (a[0] < b[0] + b[2] - pad and b[0] < a[0] + a[2] - pad
            and a[1] < b[1] + b[3] - pad and b[1] < a[1] + a[3] - pad)


def _inside(a, b):
    return a[0] >= b[0] and a[1] >= b[1] and a[0] + a[2] <= b[0] + b[2] and a[1] + a[3] <= b[1] + b[3]


class Diagram:
    def __init__(self, did, w=560, h=None, cap='', kcap=None, alt=None, kalt=None, minw=460, at=None):
        self.did, self.W, self.H = did, w, h
        self.cap, self.kcap = cap, kcap
        self.alt, self.kalt = alt, kalt
        self.minw, self.at = minw, at
        self.nodes, self.edges, self.groups, self.textsl, self.bars, self.arrows = {}, [], [], [], [], []

    # ---------- builders ----------
    def node(self, key, x, y, w, h, lbl, sub=None, icon=None, t='plain', k=None, ksub=None, kicon=None, lay=None):
        if key in self.nodes:
            raise ValueError(f"{self.did}: duplicate node {key}")
        n = Node(key, x, y, w, h, lbl, sub, icon, t, k, ksub, kicon, lay)
        self.nodes[key] = n
        return n

    def edge(self, a, b, lbl=None, k=None, t='n', **kw):
        e = Edge(a, b, lbl, k, t, **kw)
        self.edges.append(e)
        return e

    def group(self, x, y, w, h, lbl='', k=None, t='', solid=False, lpos='tl'):
        self.groups.append(dict(x=x, y=y, w=w, h=h, lbl=lbl, k=k, t=t, solid=solid, lpos=lpos))

    def arrow(self, p, q, t='n', dash=False, both=False):
        self.arrows.append(dict(p=p, q=q, t=t, dash=dash, both=both))

    def text(self, x, y, s, k=None, cls='sub', anchor='start'):
        self.textsl.append(dict(x=x, y=y, s=s, k=k, cls=cls, anchor=anchor))

    def bar(self, x, y, w, h, lbl='', k=None, t=''):
        self.bars.append(dict(x=x, y=y, w=w, h=h, lbl=lbl, k=k, t=t))

    # ---------- geometry ----------
    def height(self):
        if self.H:
            return self.H
        ys = [n.y + n.h for n in self.nodes.values()]
        ys += [g['y'] + g['h'] for g in self.groups]
        ys += [b['y'] + b['h'] for b in self.bars]
        ys += [t['y'] + 6 for t in self.textsl]
        for e in self.edges:
            for p in route(e, self.nodes[e.a], self.nodes[e.b]):
                ys.append(p[1])
        for a in self.arrows:
            ys += [a['p'][1], a['q'][1]]
        return int(max(ys) + 12)

    def _node_layout(self, n, kid):
        """Return (icon_pos or None, text items [(cls, x, y, s, anchor)], avail_w, need_h)."""
        lbl, sub, icon = n.texts(kid)
        ll = lbl.split('\n') if lbl else []
        sl = sub.split('\n') if sub else []
        blockh = 17 * len(ll) + 15 * len(sl)
        lay = n.lay or ('top' if icon and n.h >= 64 and n.w < 2.2 * n.h else ('side' if icon else 'center'))
        items = []
        if lay == 'side':
            ix, iy = n.x + 12, n.y + n.h / 2 - 11
            tx, anchor, avail = n.x + 44, 'start', n.w - 44 - 8
            top = n.y + (n.h - blockh) / 2
            need_h = max(blockh, 22) + 10
        elif lay == 'top':
            ix, iy = n.x + n.w / 2 - 11, n.y + 8
            tx, anchor, avail = n.x + n.w / 2, 'middle', n.w - 14
            top = n.y + 34
            need_h = 34 + blockh + 6
        else:
            ix = iy = None
            tx, anchor, avail = n.x + n.w / 2, 'middle', n.w - 14
            top = n.y + (n.h - blockh) / 2
            need_h = blockh + 10
        y = top
        for s in ll:
            items.append(('lbl', tx, y + 13, s, anchor))
            y += 17
        for s in sl:
            items.append(('sub', tx, y + 11.5, s, anchor))
            y += 15
        ipos = (ix, iy, icon) if icon else None
        return ipos, items, avail, need_h

    def _label_rect(self, e, pts, kid):
        s = (e.k if (kid and e.k is not None) else e.lbl)
        if not s:
            return None, None
        segs = [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
        if e.lp is not None:
            i = e.lp if e.lp >= 0 else len(segs) + e.lp
        else:
            lens = [abs(p[0] - q[0]) + abs(p[1] - q[1]) for p, q in segs]
            i = lens.index(max(lens))
        p, q = segs[i]
        cx = p[0] + (q[0] - p[0]) * e.lo
        cy = p[1] + (q[1] - p[1]) * e.lo
        w = text_w(s, ELBL) + 10
        return (cx - w / 2, cy - 9.5, w, 19), s

    # ---------- render ----------
    def svg(self, kid=False):
        W, H = self.W, self.height()
        mid = self.did.replace(':', '-') + ('-k' if kid else '')
        types = sorted({e.t for e in self.edges} | {a['t'] for a in self.arrows})
        out = []
        alt = (self.kalt or self.kcap or self.cap) if kid else (self.alt or self.cap)
        out.append(f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{esc(_plain(alt))}" style="min-width:{self.minw}px">')
        if types:
            out.append('<defs>')
            for t in types:
                out.append(f'<marker id="ah-{mid}-{t}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path class="ah ah-{t}" d="M0 0L10 5L0 10z"/></marker>')
            out.append('</defs>')
        for g in self.groups:
            cls = 'grp' + (f' g-{g["t"]}' if g['t'] else '') + (' g-solid' if g['solid'] else '')
            out.append(f'<rect class="{cls}" x="{g["x"]}" y="{g["y"]}" width="{g["w"]}" height="{g["h"]}" rx="10"/>')
            lab = g['k'] if (kid and g['k'] is not None) else g['lbl']
            if lab:
                gx, gy, ga = _glabel_pos(g, lab)
                out.append(f'<text class="glbl" x="{gx:.1f}" y="{gy:.1f}" text-anchor="{ga}">{esc(lab)}</text>')
        for b in self.bars:
            cls = 'bar' + (f' b-{b["t"]}' if b['t'] else '')
            out.append(f'<rect class="{cls}" x="{b["x"]}" y="{b["y"]}" width="{b["w"]}" height="{b["h"]}" rx="4"/>')
            lab = b['k'] if (kid and b['k'] is not None) else b['lbl']
            if lab:
                out.append(f'<text class="blbl" x="{b["x"] + b["w"] / 2:.1f}" y="{b["y"] + b["h"] / 2 + 5:.1f}" text-anchor="middle">{esc(lab)}</text>')
        for a in self.arrows:
            cls = f'edge e-{a["t"]}' + (' dash' if a['dash'] else '')
            ms = f' marker-start="url(#ah-{mid}-{a["t"]})"' if a['both'] else ''
            out.append(f'<path class="{cls}" d="M{a["p"][0]} {a["p"][1]} L{a["q"][0]} {a["q"][1]}" marker-end="url(#ah-{mid}-{a["t"]})"{ms}/>')
        labels = []
        for e in self.edges:
            A, B = self.nodes[e.a], self.nodes[e.b]
            pts = route(e, A, B)
            d = 'M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in pts)
            cls = f'edge e-{e.t}' + (' dash' if e.dash else '')
            ms = f' marker-start="url(#ah-{mid}-{e.t})"' if e.both else ''
            out.append(f'<path class="{cls}" d="{d}" marker-end="url(#ah-{mid}-{e.t})"{ms}/>')
            r, s = self._label_rect(e, pts, kid)
            if r:
                labels.append((r, s))
        for r, s in labels:
            out.append(f'<rect class="elbg" x="{r[0]:.1f}" y="{r[1]:.1f}" width="{r[2]:.1f}" height="{r[3]}" rx="3"/>')
            out.append(f'<text class="elbl" x="{r[0] + r[2] / 2:.1f}" y="{r[1] + 14:.1f}" text-anchor="middle">{esc(s)}</text>')
        for n in self.nodes.values():
            ipos, items, _, _ = self._node_layout(n, kid)
            out.append(f'<g class="n t-{n.t}"><rect class="n-box" x="{n.x}" y="{n.y}" width="{n.w}" height="{n.h}" rx="8"/>')
            if ipos:
                ix, iy, icon = ipos
                if icon not in ICONS:
                    raise KeyError(f"{self.did}: unknown icon {icon}")
                out.append(f'<g class="ico" transform="translate({ix:.1f} {iy:.1f}) scale(0.917)">{ICONS[icon]}</g>')
            for cls, x, y, s, anchor in items:
                a = f' text-anchor="{anchor}"' if anchor != 'start' else ''
                out.append(f'<text class="{cls}" x="{x:.1f}" y="{y:.1f}"{a}>{esc(s)}</text>')
            out.append('</g>')
        for t in self.textsl:
            s = t['k'] if (kid and t['k'] is not None) else t['s']
            out.append(f'<text class="{t["cls"]}" x="{t["x"]}" y="{t["y"]}" text-anchor="{t["anchor"]}">{esc(s)}</text>')
        out.append('</svg>')
        return ''.join(out)

    def figure(self, kid=False, cap_html=None):
        cap = cap_html if cap_html is not None else esc((self.kcap or self.cap) if kid else self.cap)
        cls = 'dg dg-kid' if kid else 'dg'
        return (f'<figure class="{cls}"><div class="dg-scroll">{self.svg(kid)}</div>'
                f'<figcaption>{cap}<span class="dg-hint"> (옆으로 밀어서 보기)</span></figcaption></figure>')

    # ---------- checks ----------
    def check(self):
        warns = []
        for kid in (False, True):
            tag = self.did + (' [비유]' if kid else '')
            W, H = self.W, self.height()
            boxes = {k: n.rect() for k, n in self.nodes.items()}
            # node text fit
            for n in self.nodes.values():
                ipos, items, avail, need_h = self._node_layout(n, kid)
                for cls, x, y, s, anchor in items:
                    size, bold = (LBL, True) if cls == 'lbl' else (SUB, False)
                    if text_w(s, size, bold) > avail:
                        warns.append(f'{tag}: text too wide in {n.key}: "{s}" ({text_w(s, size, bold):.0f} > {avail:.0f})')
                if need_h > n.h + 0.5:
                    warns.append(f'{tag}: node {n.key} too short ({n.h} < {need_h:.0f})')
                if kid and n.k is None and _has_latin(n.lbl):
                    warns.append(f'{tag}: node {n.key} keeps formal label "{n.lbl}" (give k=)')
                lbl, sub, _ = n.texts(kid)
                if kid and (_has_latin(lbl or '') or _has_latin(sub or '')):
                    warns.append(f'{tag}: English left in analogy label of {n.key}: "{lbl}" / "{sub}"')
            # node overlaps
            keys = list(boxes)
            for i in range(len(keys)):
                for j in range(i + 1, len(keys)):
                    if _ov(boxes[keys[i]], boxes[keys[j]]):
                        warns.append(f'{tag}: nodes overlap {keys[i]} / {keys[j]}')
            # bounds
            for k, r in boxes.items():
                if r[0] < 2 or r[1] < 2 or r[0] + r[2] > W - 2 or r[1] + r[3] > H - 2:
                    warns.append(f'{tag}: node {k} outside viewBox')
            for g in self.groups:
                if g['x'] < 2 or g['y'] < 2 or g['x'] + g['w'] > W - 2 or g['y'] + g['h'] > H - 2:
                    warns.append(f'{tag}: group "{g["lbl"]}" outside viewBox')
                lab = g['k'] if (kid and g['k'] is not None) else g['lbl']
                if lab:
                    gx, gy, ga = _glabel_pos(g, lab)
                    tw = text_w(lab, GLBL, True)
                    lr = (gx - (tw if ga == 'end' else 0), gy - 13, tw, 17)
                    if lr[0] + lr[2] > g['x'] + g['w'] - 6:
                        warns.append(f'{tag}: group label too wide "{lab}"')
                    for k, r in boxes.items():
                        if _ov(lr, r):
                            warns.append(f'{tag}: group label "{lab}" covers node {k}')
                    for e in self.edges:
                        pts = route(e, self.nodes[e.a], self.nodes[e.b])
                        for i in range(len(pts) - 1):
                            if _seg_hits_rect(pts[i], pts[i + 1], lr, pad=1):
                                warns.append(f'{tag}: edge {e.a}->{e.b} runs through group label "{lab}"')
                                break
                    if kid and _has_latin(lab):
                        warns.append(f'{tag}: English left in group label "{lab}"')
            # edges and labels
            lrects = []
            paths = []
            for idx, e in enumerate(self.edges):
                A, B = self.nodes[e.a], self.nodes[e.b]
                pts = route(e, A, B)
                paths.append((idx, e, pts))
                r, s = self._label_rect(e, pts, kid)
                if r:
                    lrects.append((idx, r, s))
                    if r[0] < 2 or r[1] < 2 or r[0] + r[2] > W - 2 or r[1] + r[3] > H - 2:
                        warns.append(f'{tag}: edge label "{s}" outside viewBox')
                    for k, nr in boxes.items():
                        if _ov(r, nr):
                            warns.append(f'{tag}: edge label "{s}" covers node {k}')
                    if kid and e.k is None and _has_latin(e.lbl or ''):
                        warns.append(f'{tag}: English left in edge label "{e.lbl}" (give k=)')
                for i in range(len(pts) - 1):
                    for k, nr in boxes.items():
                        if k in (e.a, e.b):
                            continue
                        if _seg_hits_rect(pts[i], pts[i + 1], nr, pad=1.5):
                            warns.append(f'{tag}: edge {e.a}->{e.b} crosses node {k}')
                for p in pts:
                    if p[0] < 0 or p[1] < 0 or p[0] > W or p[1] > H:
                        warns.append(f'{tag}: edge {e.a}->{e.b} leaves viewBox')
            for i in range(len(lrects)):
                for j in range(i + 1, len(lrects)):
                    if _ov(lrects[i][1], lrects[j][1]):
                        warns.append(f'{tag}: edge labels overlap "{lrects[i][2]}" / "{lrects[j][2]}"')
            for idx, e, pts in paths:
                for jdx, r, s in lrects:
                    if jdx == idx:
                        continue
                    for i in range(len(pts) - 1):
                        if _seg_hits_rect(pts[i], pts[i + 1], r, pad=2):
                            warns.append(f'{tag}: edge {e.a}->{e.b} runs through label "{s}"')
                            break
            # free text
            trs = []
            for t in self.textsl:
                s = t['k'] if (kid and t['k'] is not None) else t['s']
                size = LBL if 'lbl' in t['cls'] else SUB
                w = text_w(s, size, 'lbl' in t['cls'])
                x0 = t['x'] - (w / 2 if t['anchor'] == 'middle' else (w if t['anchor'] == 'end' else 0))
                r = (x0, t['y'] - size * 0.85, w, size * 1.1)
                trs.append((r, s))
                if r[0] < 2 or r[0] + r[2] > W - 2 or r[1] < 2 or r[1] + r[3] > H - 2:
                    warns.append(f'{tag}: text "{s}" outside viewBox')
                for k, nr in boxes.items():
                    if _ov(r, nr):
                        warns.append(f'{tag}: text "{s}" covers node {k}')
                for jdx, lr, ls in lrects:
                    if _ov(r, lr):
                        warns.append(f'{tag}: text "{s}" overlaps edge label "{ls}"')
                if kid and t['k'] is None and _has_latin(t['s']):
                    warns.append(f'{tag}: English left in text "{t["s"]}" (give k=)')
            for i in range(len(trs)):
                for j in range(i + 1, len(trs)):
                    if _ov(trs[i][0], trs[j][0]):
                        warns.append(f'{tag}: texts overlap "{trs[i][1]}" / "{trs[j][1]}"')
            for b in self.bars:
                lab = b['k'] if (kid and b['k'] is not None) else b['lbl']
                if lab and text_w(lab, LBL, True) > b['w'] - 8:
                    warns.append(f'{tag}: bar label too wide "{lab}"')
                if kid and b['k'] is None and _has_latin(b['lbl'] or ''):
                    warns.append(f'{tag}: English left in bar "{b["lbl"]}"')
        return sorted(set(warns))


def _glabel_pos(g, lab):
    if g.get('lpos') == 'bl':
        return g['x'] + 12, g['y'] + g['h'] - 9, 'start'
    if g.get('lpos') == 'tr':
        return g['x'] + g['w'] - 12, g['y'] + 19, 'end'
    if g.get('lpos') == 'br':
        return g['x'] + g['w'] - 12, g['y'] + g['h'] - 9, 'end'
    return g['x'] + 12, g['y'] + 19, 'start'


def _has_latin(s):
    import re
    return bool(re.search(r'[A-Za-z]{2,}', s or ''))


def _plain(s):
    import re
    return re.sub(r'<[^>]+>', '', s or '')
