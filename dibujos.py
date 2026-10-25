"""Motor de dibujo SVG (solo Pillow + numpy) para las ilustraciones de los Shorts.

Soporta:
  - Formas: circle, ellipse, rect (rx/ry), line, polyline, polygon, path (M L H V C S Q T A Z,
    absolutos y relativos). Varias subrutas en un path se combinan con regla par-impar (huecos).
  - Pintura: colores (#hex, rgb(), nombres), linearGradient y radialGradient (con <stop>,
    objectBoundingBox o userSpaceOnUse, href a otro degradado), fill/stroke-opacity, opacity
    de elemento y de grupo, stroke-width, style="...".
  - transform (translate, scale, rotate, matrix, skewX/Y), <defs>, clip-path="url(#id)".
  - Partes animadas: <g data-anim="TIPO" data-origen="x y" data-periodo="s" data-amplitud="n"
    data-fase="s">. TIPO: flotar, balancear, girar, latir, parpadear, brillar.
No soporta texto, filtros, máscaras ni patrones.

    from dibujos import Ilustracion, render_svg
    il = Ilustracion(svg, 480)        # capas listas para animar
    img = il.frame(t)                  # PIL RGBA en el segundo t
    img = render_svg(svg, 480)         # imagen fija (t = 0)
"""
import math, re
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image, ImageDraw

SS = 3  # supermuestreo para suavizar bordes

NAMED = {"black": "#000000", "white": "#ffffff", "red": "#ff0000", "green": "#008000", "blue": "#0000ff",
         "yellow": "#ffff00", "orange": "#ffa500", "purple": "#800080", "pink": "#ffc0cb", "brown": "#8b4513",
         "gray": "#808080", "grey": "#808080", "cyan": "#00ffff", "magenta": "#ff00ff", "gold": "#ffd700",
         "navy": "#000080", "teal": "#008080", "lime": "#00ff00", "skyblue": "#87ceeb", "beige": "#f5f5dc",
         "tan": "#d2b48c", "salmon": "#fa8072", "coral": "#ff7f50", "silver": "#c0c0c0", "olive": "#808000",
         "maroon": "#800000", "darkgreen": "#006400", "lightblue": "#add8e6", "lightgreen": "#90ee90"}
NUM = r"[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?"

def parse_color(v):
    if v is None: return None
    v = v.strip().lower()
    if v in ("none", "transparent", ""): return None
    v = NAMED.get(v, v)
    if v.startswith("#"):
        h = v[1:]
        if len(h) in (3, 4): h = "".join(c * 2 for c in h[:3])
        try: return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
        except ValueError: return (0, 0, 0)
    m = re.match(r"rgba?\(([^)]+)\)", v)
    if m:
        p = [float(x.strip().rstrip("%")) for x in m.group(1).split(",")[:3]]
        return tuple(int(max(0, min(255, x))) for x in p)
    return (0, 0, 0)

def num_list(s):
    return [float(x) for x in re.findall(NUM, s or "")]

def fnum(v, default=0.0):
    n = num_list(str(v)) if v is not None else []
    if not n: return default
    return n[0] / 100 if str(v).strip().endswith("%") else n[0]

# ---------- matrices afines (a, b, c, d, e, f) ----------
I = (1, 0, 0, 1, 0, 0)
def mul(m1, m2):
    a1, b1, c1, d1, e1, f1 = m1; a2, b2, c2, d2, e2, f2 = m2
    return (a1 * a2 + c1 * b2, b1 * a2 + d1 * b2, a1 * c2 + c1 * d2, b1 * c2 + d1 * d2,
            a1 * e2 + c1 * f2 + e1, b1 * e2 + d1 * f2 + f1)

def inv(m):
    a, b, c, d, e, f = m; det = a * d - b * c or 1e-9
    return (d / det, -b / det, -c / det, a / det, (c * f - d * e) / det, (b * e - a * f) / det)

def parse_transform(s):
    m = I
    for name, args in re.findall(r"([a-zA-Z]+)\s*\(([^)]*)\)", s or ""):
        a = num_list(args)
        if not a: continue
        if name == "translate": t = (1, 0, 0, 1, a[0], a[1] if len(a) > 1 else 0)
        elif name == "scale": t = (a[0], 0, 0, a[1] if len(a) > 1 else a[0], 0, 0)
        elif name == "rotate":
            r = math.radians(a[0]); co, si = math.cos(r), math.sin(r); t = (co, si, -si, co, 0, 0)
            if len(a) >= 3: t = mul(mul((1, 0, 0, 1, a[1], a[2]), t), (1, 0, 0, 1, -a[1], -a[2]))
        elif name == "matrix" and len(a) == 6: t = tuple(a)
        elif name == "skewX": t = (1, 0, math.tan(math.radians(a[0])), 1, 0, 0)
        elif name == "skewY": t = (1, math.tan(math.radians(a[0])), 0, 1, 0, 0)
        else: continue
        m = mul(m, t)
    return m

def apply(m, pts):
    a, b, c, d, e, f = m
    return [(a * x + c * y + e, b * x + d * y + f) for x, y in pts]

def mscale(m):
    return math.sqrt(abs(m[0] * m[3] - m[1] * m[2])) or 1.0

# ---------- geometría ----------
def ellipse_pts(cx, cy, rx, ry, n=96):
    return [(cx + rx * math.cos(2 * math.pi * i / n), cy + ry * math.sin(2 * math.pi * i / n)) for i in range(n)]

def rect_pts(x, y, w, h, rx, ry):
    if rx <= 0 and ry <= 0: return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
    rx = min(rx or ry, w / 2); ry = min(ry or rx, h / 2); pts = []
    for cx, cy, a0 in ((x + w - rx, y + ry, -90), (x + w - rx, y + h - ry, 0), (x + rx, y + h - ry, 90), (x + rx, y + ry, 180)):
        for i in range(12):
            a = math.radians(a0 + 90 * i / 11); pts.append((cx + rx * math.cos(a), cy + ry * math.sin(a)))
    return pts

def cubic(p0, p1, p2, p3, n=24):
    out = []
    for i in range(1, n + 1):
        t = i / n; u = 1 - t
        out.append((u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
                    u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1]))
    return out

def quad(p0, p1, p2, n=18):
    out = []
    for i in range(1, n + 1):
        t = i / n; u = 1 - t
        out.append((u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0], u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1]))
    return out

def arc(p0, rx, ry, phi, large, sweep, p1):
    if rx == 0 or ry == 0 or p0 == p1: return [p1]
    rx, ry = abs(rx), abs(ry); ph = math.radians(phi); co, si = math.cos(ph), math.sin(ph)
    dx, dy = (p0[0] - p1[0]) / 2, (p0[1] - p1[1]) / 2
    x1 = co * dx + si * dy; y1 = -si * dx + co * dy
    lam = x1 ** 2 / rx ** 2 + y1 ** 2 / ry ** 2
    if lam > 1: s = math.sqrt(lam); rx *= s; ry *= s
    num = rx ** 2 * ry ** 2 - rx ** 2 * y1 ** 2 - ry ** 2 * x1 ** 2
    den = rx ** 2 * y1 ** 2 + ry ** 2 * x1 ** 2
    k = math.sqrt(max(0, num / den)) if den else 0
    if large == sweep: k = -k
    cxp = k * rx * y1 / ry; cyp = -k * ry * x1 / rx
    cx = co * cxp - si * cyp + (p0[0] + p1[0]) / 2; cy = si * cxp + co * cyp + (p0[1] + p1[1]) / 2
    ang = lambda u, v: math.atan2(u[0] * v[1] - u[1] * v[0], u[0] * v[0] + u[1] * v[1])
    v1 = ((x1 - cxp) / rx, (y1 - cyp) / ry); v2 = ((-x1 - cxp) / rx, (-y1 - cyp) / ry)
    t1 = ang((1, 0), v1); dt = ang(v1, v2)
    if not sweep and dt > 0: dt -= 2 * math.pi
    elif sweep and dt < 0: dt += 2 * math.pi
    n = max(8, int(abs(dt) / (math.pi / 32)))
    return [(cx + rx * math.cos(t1 + dt * i / n) * co - ry * math.sin(t1 + dt * i / n) * si,
             cy + rx * math.cos(t1 + dt * i / n) * si + ry * math.sin(t1 + dt * i / n) * co) for i in range(1, n + 1)]

def path_subpaths(d):
    toks = re.findall(r"[MmLlHhVvCcSsQqTtAaZz]|" + NUM, d or "")
    subs = []; cur = []
    x = y = sx = sy = 0.0; i = 0; cmd = None; last_c = last_q = None
    def nums(k):
        nonlocal i
        vals = [float(toks[i + j]) for j in range(k)]; i += k; return vals
    while i < len(toks):
        if re.match(r"[A-Za-z]", toks[i]): cmd = toks[i]; i += 1
        elif cmd is None: i += 1; continue
        rel = cmd.islower(); C = cmd.upper()
        try:
            if C == "Z":
                if cur: subs.append((cur, True))
                cur = []; x, y = sx, sy; last_c = last_q = None; continue
            if C == "M":
                a, b = nums(2)
                if rel: a += x; b += y
                if cur: subs.append((cur, False))
                x, y = a, b; sx, sy = x, y; cur = [(x, y)]
                cmd = "l" if rel else "L"; last_c = last_q = None; continue
            if not cur: cur = [(x, y)]
            if C == "L":
                a, b = nums(2)
                if rel: a += x; b += y
                x, y = a, b; cur.append((x, y)); last_c = last_q = None
            elif C == "H":
                a, = nums(1); x = x + a if rel else a; cur.append((x, y)); last_c = last_q = None
            elif C == "V":
                b, = nums(1); y = y + b if rel else b; cur.append((x, y)); last_c = last_q = None
            elif C in "CS":
                if C == "C":
                    x1, y1, x2, y2, a, b = nums(6)
                    if rel: x1 += x; y1 += y; x2 += x; y2 += y; a += x; b += y
                else:
                    x2, y2, a, b = nums(4)
                    if rel: x2 += x; y2 += y; a += x; b += y
                    x1, y1 = (2 * x - last_c[0], 2 * y - last_c[1]) if last_c else (x, y)
                cur += cubic((x, y), (x1, y1), (x2, y2), (a, b)); last_c = (x2, y2); last_q = None; x, y = a, b
            elif C in "QT":
                if C == "Q":
                    x1, y1, a, b = nums(4)
                    if rel: x1 += x; y1 += y; a += x; b += y
                else:
                    a, b = nums(2)
                    if rel: a += x; b += y
                    x1, y1 = (2 * x - last_q[0], 2 * y - last_q[1]) if last_q else (x, y)
                cur += quad((x, y), (x1, y1), (a, b)); last_q = (x1, y1); last_c = None; x, y = a, b
            elif C == "A":
                rx, ry, phi, la, sw, a, b = nums(7)
                if rel: a += x; b += y
                cur += arc((x, y), rx, ry, phi, int(la), int(sw), (a, b)); x, y = a, b; last_c = last_q = None
            else:
                i += 1
        except (IndexError, ValueError):
            break
    if cur: subs.append((cur, False))
    return subs

# ---------- motor ----------
INHERIT = ("fill", "stroke", "stroke-width", "fill-opacity", "stroke-opacity", "fill-rule")
ANIMS = ("flotar", "balancear", "girar", "latir", "parpadear", "brillar")

class Motor:
    def __init__(self, root, size):
        vb = num_list(root.get("viewBox"))
        if len(vb) != 4:
            w = num_list(root.get("width")) or [400]; h = num_list(root.get("height")) or [400]; vb = [0, 0, w[0], h[0]]
        vx, vy, vw, vh = vb
        self.k = size / max(vw, vh)
        self.W, self.H = max(1, int(round(vw * self.k))), max(1, int(round(vh * self.k)))
        self.BW, self.BH = self.W * SS, self.H * SS
        self.base = (self.k * SS, 0, 0, self.k * SS, -vx * self.k * SS, -vy * self.k * SS)
        self.defs = {}
        for el in root.iter():
            if el.get("id"): self.defs[el.get("id")] = el
        self.root = root

    # --- pintura ---
    def _ref(self, v):
        m = re.match(r"url\(\s*#([^)\s]+)\s*\)", (v or "").strip())
        return self.defs.get(m.group(1)) if m else None

    def _stops(self, g, seen=0):
        stops = []
        for s in g:
            if s.tag.split("}")[-1] != "stop": continue
            st = {}
            for decl in (s.get("style") or "").split(";"):
                if ":" in decl: k, v = decl.split(":", 1); st[k.strip()] = v.strip()
            col = parse_color(s.get("stop-color", st.get("stop-color", "#000"))) or (0, 0, 0)
            op = fnum(s.get("stop-opacity", st.get("stop-opacity", 1)), 1)
            stops.append((max(0, min(1, fnum(s.get("offset", 0)))), col, op))
        if not stops and seen < 4:
            href = g.get("href") or g.get("{http://www.w3.org/1999/xlink}href")
            if href and href[1:] in self.defs: return self._stops(self.defs[href[1:]], seen + 1)
        stops.sort(key=lambda s: s[0])
        return stops or [(0, (0, 0, 0), 1)]

    def _gradient(self, g, m, ubbox, box):
        """Devuelve un array (h, w, 4) float con el degradado sobre la caja de píxeles box."""
        x0, y0, x1, y1 = box
        ys, xs = np.mgrid[y0:y1, x0:x1].astype(np.float64) + 0.5
        a, b, c, d, e, f = inv(m)
        ux = a * xs + c * ys + e; uy = b * xs + d * ys + f            # coordenadas de usuario
        units = g.get("gradientUnits", "objectBoundingBox")
        gt = parse_transform(g.get("gradientTransform"))
        if units != "userSpaceOnUse":
            bx, by, bw, bh = ubbox; bw = bw or 1; bh = bh or 1
            ux, uy = (ux - bx) / bw, (uy - by) / bh
        if gt != I:
            a2, b2, c2, d2, e2, f2 = inv(gt); ux, uy = a2 * ux + c2 * uy + e2, b2 * ux + d2 * uy + f2
        tag = g.tag.split("}")[-1]
        dflt = (lambda v, dv: fnum(g.get(v), dv)) if units != "userSpaceOnUse" else (lambda v, dv: fnum(g.get(v), dv))
        if tag == "linearGradient":
            gx1, gy1 = dflt("x1", 0.0), dflt("y1", 0.0); gx2, gy2 = dflt("x2", 1.0), dflt("y2", 0.0)
            dx, dy = gx2 - gx1, gy2 - gy1; L = dx * dx + dy * dy or 1e-9
            t = ((ux - gx1) * dx + (uy - gy1) * dy) / L
        else:
            cx, cy, r = dflt("cx", 0.5), dflt("cy", 0.5), dflt("r", 0.5) or 1e-9
            t = np.sqrt((ux - cx) ** 2 + (uy - cy) ** 2) / r
        t = np.clip(t, 0, 1)
        stops = self._stops(g)
        offs = [s[0] for s in stops]
        out = np.empty(t.shape + (4,))
        for ch in range(3): out[..., ch] = np.interp(t, offs, [s[1][ch] for s in stops])
        out[..., 3] = np.interp(t, offs, [s[2] for s in stops])
        return out

    # --- máscaras ---
    def _mask(self, polys, box, evenodd):
        x0, y0, x1, y1 = box
        if len(polys) == 1:
            mk = Image.new("L", (x1 - x0, y1 - y0), 0)
            p = [(px - x0, py - y0) for px, py in polys[0]]
            if len(p) >= 3: ImageDraw.Draw(mk).polygon(p, fill=255)
            return np.asarray(mk, np.float64) / 255
        acc = np.zeros((y1 - y0, x1 - x0), bool)
        for poly in polys:
            if len(poly) < 3: continue
            mk = Image.new("L", (x1 - x0, y1 - y0), 0)
            ImageDraw.Draw(mk).polygon([(px - x0, py - y0) for px, py in poly], fill=255)
            acc ^= np.asarray(mk) > 127
        return acc.astype(np.float64)

    def _stroke_mask(self, polys, closed, w, box):
        x0, y0, x1, y1 = box
        mk = Image.new("L", (x1 - x0, y1 - y0), 0); d = ImageDraw.Draw(mk); r = w / 2
        for p, c in zip(polys, closed):
            if len(p) < 2: continue
            q = [(px - x0, py - y0) for px, py in p]
            if c: q = q + [q[0], q[1] if len(q) > 1 else q[0]]
            d.line(q, fill=255, width=max(1, int(round(w))), joint="curve")
            for (ex, ey) in ([q[0], q[-1]] if not c else []):
                d.ellipse((ex - r, ey - r, ex + r, ey + r), fill=255)
        return np.asarray(mk, np.float64) / 255

    def _clip(self, el, m):
        cp = self._ref(el.get("clip-path"))
        if cp is None: return None
        mk = Image.new("L", (self.BW, self.BH), 0); d = ImageDraw.Draw(mk)
        cm = mul(m, parse_transform(cp.get("transform")))
        for ch in cp.iter():
            if ch is cp: continue
            g = self._geom(ch, mul(cm, parse_transform(ch.get("transform"))))
            if g:
                for poly in g[0]:
                    if len(poly) >= 3: d.polygon(poly, fill=255)
        return np.asarray(mk, np.float64) / 255

    # --- geometría de un elemento (en píxeles del lienzo grande) ---
    def _geom(self, el, m):
        tag = el.tag.split("}")[-1]
        g = lambda k, dv=0.0: fnum(el.get(k), dv)
        if tag == "circle": polys, closed = [ellipse_pts(g("cx"), g("cy"), g("r"), g("r"))], [True]
        elif tag == "ellipse": polys, closed = [ellipse_pts(g("cx"), g("cy"), g("rx"), g("ry"))], [True]
        elif tag == "rect":
            polys, closed = [rect_pts(g("x"), g("y"), g("width"), g("height"), g("rx"), g("ry"))], [True]
        elif tag == "line": polys, closed = [[(g("x1"), g("y1")), (g("x2"), g("y2"))]], [False]
        elif tag in ("polyline", "polygon"):
            v = num_list(el.get("points")); polys, closed = [list(zip(v[0::2], v[1::2]))], [tag == "polygon"]
        elif tag == "path":
            sp = path_subpaths(el.get("d"))
            if not sp: return None
            polys, closed = [p for p, _ in sp], [c for _, c in sp]
        else:
            return None
        allu = [pt for p in polys for pt in p]
        if not allu: return None
        xs = [p[0] for p in allu]; ys = [p[1] for p in allu]
        ubbox = (min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))
        return [apply(m, p) for p in polys], closed, ubbox

    def _style(self, el, inherited):
        st = {k: v for k, v in inherited.items() if k in INHERIT}
        for k in INHERIT:
            if el.get(k) is not None: st[k] = el.get(k)
        op = fnum(el.get("opacity"), 1) if el.get("opacity") is not None else 1.0
        for decl in (el.get("style") or "").split(";"):
            if ":" in decl:
                k, v = decl.split(":", 1); k = k.strip(); v = v.strip()
                if k == "opacity": op *= fnum(v, 1)
                elif k in INHERIT: st[k] = v
        return st, op

    def _paint(self, layer, paint, alpha_mask, box, m, ubbox, opacity):
        if alpha_mask.max() <= 0: return
        x0, y0, x1, y1 = box
        ref = self._ref(paint)
        if ref is not None and ref.tag.split("}")[-1] in ("linearGradient", "radialGradient"):
            grad = self._gradient(ref, m, ubbox, box)
            rgb = grad[..., :3]; a = grad[..., 3] * alpha_mask * opacity
        else:
            col = parse_color(paint)
            if col is None:
                if ref is None: return
                col = (0, 0, 0)
            rgb = np.broadcast_to(np.array(col, np.float64), alpha_mask.shape + (3,)); a = alpha_mask * opacity
        arr = np.dstack([rgb, a * 255]).clip(0, 255).astype(np.uint8)
        layer.alpha_composite(Image.fromarray(arr, "RGBA"), (x0, y0))

    def _box(self, polys, pad):
        xs = [p[0] for poly in polys for p in poly]; ys = [p[1] for poly in polys for p in poly]
        x0 = max(0, int(math.floor(min(xs) - pad))); y0 = max(0, int(math.floor(min(ys) - pad)))
        x1 = min(self.BW, int(math.ceil(max(xs) + pad)) + 1); y1 = min(self.BH, int(math.ceil(max(ys) + pad)) + 1)
        return (x0, y0, x1, y1) if x1 > x0 and y1 > y0 else None

    def draw_shape(self, layer, el, m, st, op, clip):
        g = self._geom(el, m)
        if not g: return
        polys, closed, ubbox = g
        tag = el.tag.split("}")[-1]
        fill = st.get("fill", "#000000") if tag not in ("line",) else "none"
        if tag == "polyline" and el.get("fill") is None and "fill" not in (el.get("style") or ""): fill = st.get("fill", "#000000")
        stroke = st.get("stroke", "none")
        sw = fnum(st.get("stroke-width", 1), 1) * mscale(m)
        pad = sw + 2
        box = self._box(polys, pad)
        if box is None: return
        x0, y0, x1, y1 = box
        cl = clip[y0:y1, x0:x1] if clip is not None else 1.0
        if fill and fill.strip().lower() != "none":
            mk = self._mask(polys, box, True)
            self._paint(layer, fill, mk * cl, box, m, ubbox, op * fnum(st.get("fill-opacity", 1), 1))
        if stroke and stroke.strip().lower() != "none" and sw > 0:
            mk = self._stroke_mask(polys, closed, sw, box)
            self._paint(layer, stroke, mk * cl, box, m, ubbox, op * fnum(st.get("stroke-opacity", 1), 1))

    def draw(self, layer, el, m, st, clip=None, on_anim=None):
        tag = el.tag.split("}")[-1]
        if tag in ("defs", "clipPath", "linearGradient", "radialGradient", "stop", "title", "desc", "metadata", "style", "mask", "filter", "pattern", "symbol", "text"):
            return
        m = mul(m, parse_transform(el.get("transform")))
        st, op = self._style(el, st)
        c2 = self._clip(el, m)
        if c2 is not None: clip = c2 if clip is None else clip * c2
        if tag in ("svg", "g", "a"):
            if on_anim is not None and el.get("data-anim") in ANIMS:
                on_anim(el, m, st, op, clip); return
            if op < 0.999:
                sub = Image.new("RGBA", (self.BW, self.BH), (0, 0, 0, 0))
                for ch in el: self.draw(sub, ch, m, st, clip, on_anim)
                sub.putalpha(sub.getchannel("A").point(lambda v: int(v * op)))
                layer.alpha_composite(sub)
            else:
                for ch in el: self.draw(layer, ch, m, st, clip, on_anim)
        elif tag == "use":
            href = el.get("href") or el.get("{http://www.w3.org/1999/xlink}href")
            if href and href[1:] in self.defs:
                mm = mul(m, (1, 0, 0, 1, fnum(el.get("x")), fnum(el.get("y"))))
                self.draw(layer, self.defs[href[1:]], mm, st, clip, on_anim)
        else:
            self.draw_shape(layer, el, m, st, op, clip)

class Ilustracion:
    """Dibujo SVG dividido en capas fijas y capas animadas, listo para componer en cualquier instante."""
    def __init__(self, svg, size):
        root = ET.fromstring(svg)
        self.mo = mo = Motor(root, size)
        self.capas = []                       # (imagen, anim | None)
        cur = [Image.new("RGBA", (mo.BW, mo.BH), (0, 0, 0, 0))]
        class Destino:                        # siempre dibuja en la capa fija actual
            def alpha_composite(self, im, dest=(0, 0)): cur[0].alpha_composite(im, dest)
        def flush():
            self.capas.append((cur[0].resize((mo.W, mo.H), Image.LANCZOS), None))
            cur[0] = Image.new("RGBA", (mo.BW, mo.BH), (0, 0, 0, 0))
        def on_anim(el, m, st, op, clip):
            flush()
            lay = Image.new("RGBA", (mo.BW, mo.BH), (0, 0, 0, 0))
            for ch in el: mo.draw(lay, ch, m, st, clip, None)
            if op < 0.999: lay.putalpha(lay.getchannel("A").point(lambda v: int(v * op)))
            o = num_list(el.get("data-origen"))
            if len(o) < 2:   # centro de la parte animada
                bb = lay.getbbox() or (0, 0, mo.BW, mo.BH)
                ox, oy = (bb[0] + bb[2]) / 2 / SS, (bb[1] + bb[3]) / 2 / SS
            else:
                ox, oy = apply(m, [(o[0], o[1])])[0]; ox /= SS; oy /= SS
            anim = dict(tipo=el.get("data-anim"), ox=ox, oy=oy,
                        periodo=fnum(el.get("data-periodo"), 0) or None,
                        amp=fnum(el.get("data-amplitud"), 0) or None,
                        fase=fnum(el.get("data-fase"), 0), k=mo.k)
            self.capas.append((lay.resize((mo.W, mo.H), Image.LANCZOS), anim))
        mo.draw(Destino(), root, mo.base, {"fill": "#000000"}, None, on_anim)
        flush()
        self.capas = [(im, an) for im, an in self.capas if an is not None or im.getbbox()]
        self.animada = any(an for _, an in self.capas)
        self.size = (mo.W, mo.H)

    @staticmethod
    def _xf(im, ox, oy, ang=0.0, sx=1.0, sy=1.0, dx=0.0, dy=0.0):
        """Rota/escala alrededor de (ox, oy) y desplaza."""
        r = math.radians(ang); co, si = math.cos(r), math.sin(r)
        # matriz directa: T(o+d) * R * S * T(-o); Pillow necesita la inversa
        a, b, c, d = co * sx, si * sx, -si * sy, co * sy
        e = ox + dx - (a * ox + c * oy); f = oy + dy - (b * ox + d * oy)
        ia, ib, ic, id_, ie, if_ = inv((a, b, c, d, e, f))
        return im.transform(im.size, Image.AFFINE, (ia, ic, ie, ib, id_, if_), resample=Image.BICUBIC)

    def frame(self, t):
        out = Image.new("RGBA", self.size, (0, 0, 0, 0))
        for im, an in self.capas:
            if an is None: out.alpha_composite(im); continue
            tipo = an["tipo"]; tt = t + an["fase"]; ox, oy = an["ox"], an["oy"]
            if tipo == "flotar":
                P = an["periodo"] or 2.4; A = (an["amp"] or 8) * an["k"]
                out.alpha_composite(self._xf(im, ox, oy, dy=A * math.sin(2 * math.pi * tt / P)))
            elif tipo == "balancear":
                P = an["periodo"] or 2.0; A = an["amp"] or 8
                out.alpha_composite(self._xf(im, ox, oy, ang=A * math.sin(2 * math.pi * tt / P)))
            elif tipo == "girar":
                P = an["periodo"] or 6.0
                out.alpha_composite(self._xf(im, ox, oy, ang=-360 * tt / P))
            elif tipo == "latir":
                P = an["periodo"] or 1.2; A = (an["amp"] or 6) / 100
                s = 1 + A * max(0, math.sin(2 * math.pi * tt / P)) ** 2
                out.alpha_composite(self._xf(im, ox, oy, sx=s, sy=s))
            elif tipo == "parpadear":
                P = an["periodo"] or 3.0; ph = (tt % P) / P; dur = 0.16 / P
                sy = 1.0
                if ph > 1 - dur: sy = max(0.08, abs((ph - (1 - dur / 2)) / (dur / 2)))
                out.alpha_composite(self._xf(im, ox, oy, sy=sy) if sy < 0.999 else im)
            elif tipo == "brillar":
                P = an["periodo"] or 1.6; A = 0.5 + 0.5 * math.sin(2 * math.pi * tt / P)
                s = 0.85 + 0.25 * A
                tmp = self._xf(im, ox, oy, sx=s, sy=s)
                tmp.putalpha(tmp.getchannel("A").point(lambda v: int(v * (0.35 + 0.65 * A))))
                out.alpha_composite(tmp)
            else:
                out.alpha_composite(im)
        return out

def render_svg(svg, size, t=0.0):
    """Imagen RGBA fija cuyo lado mayor mide `size` píxeles."""
    return Ilustracion(svg, size).frame(t)

if __name__ == "__main__":
    import sys
    svg = open(sys.argv[1], encoding="utf-8").read()
    render_svg(svg, int(sys.argv[3]) if len(sys.argv) > 3 else 600).save(sys.argv[2])
    print(sys.argv[2])
