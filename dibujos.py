"""Intérprete SVG mínimo (solo Pillow) para los dibujos de los Shorts.

Soporta: <svg viewBox>, <g>, <circle>, <ellipse>, <rect rx>, <line>, <polyline>, <polygon>, <path>
(comandos M L H V C S Q T A Z, absolutos y relativos), atributos fill, stroke, stroke-width,
opacity, fill-opacity, stroke-opacity, style="..." y transform (translate, scale, rotate, matrix).
No soporta degradados, texto, máscaras ni agujeros dentro de una misma figura.

    from dibujos import render_svg
    img = render_svg(svg_string, 460)   # PIL RGBA de 460 px de lado mayor
"""
import math, re
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw

SS = 3  # supermuestreo para suavizar bordes

NAMED = {"black": "#000000", "white": "#ffffff", "red": "#ff0000", "green": "#008000", "blue": "#0000ff",
         "yellow": "#ffff00", "orange": "#ffa500", "purple": "#800080", "pink": "#ffc0cb", "brown": "#8b4513",
         "gray": "#808080", "grey": "#808080", "cyan": "#00ffff", "magenta": "#ff00ff", "gold": "#ffd700",
         "navy": "#000080", "teal": "#008080", "lime": "#00ff00", "skyblue": "#87ceeb", "beige": "#f5f5dc",
         "tan": "#d2b48c", "salmon": "#fa8072", "coral": "#ff7f50", "silver": "#c0c0c0", "olive": "#808000",
         "maroon": "#800000", "darkgreen": "#006400", "lightblue": "#add8e6", "lightgreen": "#90ee90"}

def parse_color(v):
    if v is None: return None
    v = v.strip().lower()
    if v in ("none", "transparent", ""): return None
    v = NAMED.get(v, v)
    if v.startswith("#"):
        h = v[1:]
        if len(h) == 3: h = "".join(c * 2 for c in h)
        if len(h) >= 6:
            try: return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
            except ValueError: return (0, 0, 0)
    m = re.match(r"rgba?\(([^)]+)\)", v)
    if m:
        p = [float(x.strip().rstrip("%")) for x in m.group(1).split(",")[:3]]
        return tuple(int(max(0, min(255, x))) for x in p)
    return (0, 0, 0)

def num_list(s):
    return [float(x) for x in re.findall(r"[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?", s or "")]

# ---------- matrices afines (a, b, c, d, e, f) como en SVG ----------
def mul(m1, m2):
    a1, b1, c1, d1, e1, f1 = m1; a2, b2, c2, d2, e2, f2 = m2
    return (a1 * a2 + c1 * b2, b1 * a2 + d1 * b2, a1 * c2 + c1 * d2, b1 * c2 + d1 * d2,
            a1 * e2 + c1 * f2 + e1, b1 * e2 + d1 * f2 + f1)

def parse_transform(s):
    m = (1, 0, 0, 1, 0, 0)
    for name, args in re.findall(r"(\w+)\s*\(([^)]*)\)", s or ""):
        a = num_list(args)
        if name == "translate": t = (1, 0, 0, 1, a[0], a[1] if len(a) > 1 else 0)
        elif name == "scale": t = (a[0], 0, 0, a[1] if len(a) > 1 else a[0], 0, 0)
        elif name == "rotate":
            r = math.radians(a[0]); co, si = math.cos(r), math.sin(r)
            t = (co, si, -si, co, 0, 0)
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
def ellipse_pts(cx, cy, rx, ry, n=72):
    return [(cx + rx * math.cos(2 * math.pi * i / n), cy + ry * math.sin(2 * math.pi * i / n)) for i in range(n)]

def rect_pts(x, y, w, h, rx, ry):
    if rx <= 0 and ry <= 0: return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
    rx = min(rx or ry, w / 2); ry = min(ry or rx, h / 2); pts = []
    for cx, cy, a0 in ((x + w - rx, y + ry, -90), (x + w - rx, y + h - ry, 0), (x + rx, y + h - ry, 90), (x + rx, y + ry, 180)):
        for i in range(10):
            a = math.radians(a0 + 90 * i / 9); pts.append((cx + rx * math.cos(a), cy + ry * math.sin(a)))
    return pts

def cubic(p0, p1, p2, p3, n=20):
    out = []
    for i in range(1, n + 1):
        t = i / n; u = 1 - t
        out.append((u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
                    u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1]))
    return out

def quad(p0, p1, p2, n=16):
    out = []
    for i in range(1, n + 1):
        t = i / n; u = 1 - t
        out.append((u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0], u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1]))
    return out

def arc(p0, rx, ry, phi, large, sweep, p1):
    """Arco elíptico SVG (endpoint -> center parametrization)."""
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
    def ang(u, v):
        a = math.atan2(u[0] * v[1] - u[1] * v[0], u[0] * v[0] + u[1] * v[1]); return a
    v1 = ((x1 - cxp) / rx, (y1 - cyp) / ry); v2 = ((-x1 - cxp) / rx, (-y1 - cyp) / ry)
    t1 = ang((1, 0), v1); dt = ang(v1, v2)
    if not sweep and dt > 0: dt -= 2 * math.pi
    elif sweep and dt < 0: dt += 2 * math.pi
    n = max(6, int(abs(dt) / (math.pi / 24)))
    out = []
    for i in range(1, n + 1):
        t = t1 + dt * i / n
        out.append((cx + rx * math.cos(t) * co - ry * math.sin(t) * si, cy + rx * math.cos(t) * si + ry * math.sin(t) * co))
    return out

def path_subpaths(d):
    toks = re.findall(r"[MmLlHhVvCcSsQqTtAaZz]|[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?", d or "")
    subs = []; cur = []; closed = []
    x = y = sx = sy = 0.0; i = 0; cmd = None; last_c = None; last_q = None
    def nums(k):
        nonlocal i
        vals = []
        for _ in range(k):
            vals.append(float(toks[i])); i += 1
        return vals
    while i < len(toks):
        if re.match(r"[A-Za-z]", toks[i]): cmd = toks[i]; i += 1
        elif cmd is None: i += 1; continue
        rel = cmd.islower(); C = cmd.upper()
        try:
            if C == "Z":
                if cur: subs.append(cur); closed.append(True)
                cur = []; x, y = sx, sy; last_c = last_q = None
                continue
            if C == "M":
                a, b = nums(2)
                if rel: a += x; b += y
                if cur: subs.append(cur); closed.append(False)
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
    if cur: subs.append(cur); closed.append(False)
    return list(zip(subs, closed))

# ---------- dibujo ----------
def _style(el, inherited):
    st = dict(inherited)
    for k in ("fill", "stroke", "stroke-width", "fill-opacity", "stroke-opacity", "stroke-linecap"):
        if el.get(k) is not None: st[k] = el.get(k)
    for decl in (el.get("style") or "").split(";"):
        if ":" in decl:
            k, v = decl.split(":", 1); k = k.strip(); v = v.strip()
            if k == "opacity":
                try: st["_op"] = float(st.get("_op", 1)) * float(v)
                except ValueError: pass
            else: st[k] = v
    return st

def _alpha(st, which):
    op = float(st.get("_op", 1))
    try: op *= float(st.get(f"{which}-opacity", 1))
    except ValueError: pass
    return int(255 * max(0, min(1, op)))

def _draw_shape(draw, polys, closed, st, m):
    fill = parse_color(st.get("fill", "#000"))
    stroke = parse_color(st.get("stroke"))
    try: sw = float(re.sub(r"[a-z%]", "", str(st.get("stroke-width", 1)))) * mscale(m)
    except ValueError: sw = mscale(m)
    tpolys = [apply(m, p) for p in polys]
    if fill is not None:
        ink = fill + (_alpha(st, "fill"),)
        for p, c in zip(tpolys, closed):
            if len(p) >= 3: draw.polygon(p, fill=ink)
    if stroke is not None and sw > 0:
        ink = stroke + (_alpha(st, "stroke"),); w = max(1, int(round(sw)))
        for p, c in zip(tpolys, closed):
            if len(p) < 2: continue
            pts = p + [p[0]] if c else p
            draw.line(pts, fill=ink, width=w, joint="curve")
            r = w / 2
            ends = [pts[0], pts[-1]] if not c else []
            for (ex, ey) in ends:
                draw.ellipse((ex - r, ey - r, ex + r, ey + r), fill=ink)

def _walk(el, draw, m, st):
    tag = el.tag.split("}")[-1]
    m = mul(m, parse_transform(el.get("transform")))
    st = _style(el, st)
    if el.get("opacity") is not None:
        st["_op"] = float(st.get("_op", 1)) * float(el.get("opacity"))
    g = lambda k, d=0.0: float(num_list(el.get(k, str(d)))[0]) if num_list(el.get(k, str(d))) else d
    if tag in ("svg", "g"):
        for ch in el: _walk(ch, draw, m, st)
    elif tag == "circle":
        _draw_shape(draw, [ellipse_pts(g("cx"), g("cy"), g("r"), g("r"))], [True], st, m)
    elif tag == "ellipse":
        _draw_shape(draw, [ellipse_pts(g("cx"), g("cy"), g("rx"), g("ry"))], [True], st, m)
    elif tag == "rect":
        _draw_shape(draw, [rect_pts(g("x"), g("y"), g("width"), g("height"), g("rx"), g("ry"))], [True], st, m)
    elif tag == "line":
        s2 = dict(st); s2["fill"] = "none"
        _draw_shape(draw, [[(g("x1"), g("y1")), (g("x2"), g("y2"))]], [False], s2, m)
    elif tag in ("polyline", "polygon"):
        v = num_list(el.get("points")); pts = list(zip(v[0::2], v[1::2]))
        s2 = dict(st)
        if tag == "polyline" and "fill" not in el.attrib and "fill:" not in (el.get("style") or ""): s2["fill"] = st.get("fill", "#000")
        _draw_shape(draw, [pts], [tag == "polygon"], s2, m)
    elif tag == "path":
        sp = path_subpaths(el.get("d"))
        if sp: _draw_shape(draw, [p for p, _ in sp], [c for _, c in sp], st, m)

def render_svg(svg, size):
    """Devuelve una imagen RGBA cuyo lado mayor mide `size` píxeles."""
    root = ET.fromstring(svg)
    vb = num_list(root.get("viewBox"))
    if len(vb) != 4:
        w = num_list(root.get("width")) or [400]; h = num_list(root.get("height")) or [400]; vb = [0, 0, w[0], h[0]]
    vx, vy, vw, vh = vb
    k = size / max(vw, vh)
    W, H = max(1, int(round(vw * k))), max(1, int(round(vh * k)))
    big = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(big, "RGBA")
    m = (k * SS, 0, 0, k * SS, -vx * k * SS, -vy * k * SS)
    _walk(root, draw, m, {"fill": "#000000"})
    return big.resize((W, H), Image.LANCZOS)

if __name__ == "__main__":
    import sys
    svg = open(sys.argv[1], encoding="utf-8").read()
    render_svg(svg, int(sys.argv[3]) if len(sys.argv) > 3 else 600).save(sys.argv[2])
    print(sys.argv[2])
