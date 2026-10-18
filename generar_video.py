"""Generador de Shorts de Mundo Curioso 5000.

Uso:
    python3 generar_video.py guiones/2026-10-19-1.json          -> videos/2026-10-19-1.mp4
    python3 generar_video.py guiones/2026-10-19-1.json --preview -> fotogramas PNG de control

El guion JSON tiene esta forma (ver guiones/ejemplo.json):
{
  "id": "2026-10-19-1",
  "paleta": 0,                       # 0-3, cambia los colores de fondo
  "gancho": ["4 curiosidades del mundo", "que te van a *sorprender*"],
  "pista": "LA ÚLTIMA ES INCREÍBLE",
  "datos": [                          # exactamente 4
    {"grande": "11", "lineas": ["husos horarios tiene *Rusia*", "..."]},
    {"grande": "60%", "contar": [0, 60, "{}%"], "lineas": ["..."]}
  ],
  "titulo": "...", "descripcion": "...", "etiquetas": ["..."]
}
Las palabras entre *asteriscos* salen resaltadas en amarillo.
"""
import json, math, os, subprocess, sys, tempfile, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

CANAL = "MUNDO CURIOSO 5000"
W, H, FPS = 1080, 1920, 30
AQUI = os.path.dirname(os.path.abspath(__file__))
SR = 44100

def load_wav(path):
    """Carga un WAV mono/estéreo como float32 mono a 44,1 kHz (None si no existe)."""
    if not os.path.exists(path): return None
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)

def _font_path(names):
    for d in ["/usr/share/fonts/opentype/inter/", "/usr/share/fonts/truetype/dejavu/"]:
        for n in names:
            if os.path.exists(d + n): return d + n
    raise SystemExit("No encuentro fuentes Inter ni DejaVu")
F_BLACK = _font_path(["InterDisplay-Black.otf", "Inter-Black.otf", "DejaVuSans-Bold.ttf"])
F_BOLD = _font_path(["InterDisplay-Bold.otf", "Inter-Bold.otf", "DejaVuSans-Bold.ttf"])

YELLOW = (255, 214, 10)
WHITE = (255, 255, 255)
RED = (230, 33, 23)
CX = 520            # centro del contenido (lejos de los botones de la derecha)
MAXW = 840

PALETAS = [
    [((20, 12, 60), (120, 20, 110)), ((8, 30, 70), (10, 110, 150)), ((5, 50, 40), (20, 130, 90)),
     ((70, 25, 10), (190, 80, 20)), ((10, 10, 40), (60, 30, 140)), ((25, 10, 50), (150, 20, 80))],
    [((10, 25, 55), (20, 90, 160)), ((60, 10, 40), (170, 30, 90)), ((20, 45, 15), (90, 140, 30)),
     ((15, 15, 60), (90, 40, 170)), ((70, 40, 5), (200, 120, 10)), ((40, 8, 20), (170, 25, 45))],
    [((40, 10, 60), (140, 40, 160)), ((5, 40, 55), (10, 130, 140)), ((65, 15, 15), (180, 50, 40)),
     ((10, 30, 70), (30, 80, 190)), ((30, 45, 10), (110, 140, 20)), ((20, 10, 45), (120, 20, 120))],
    [((5, 35, 45), (15, 110, 120)), ((50, 20, 70), (130, 50, 180)), ((70, 30, 5), (210, 100, 20)),
     ((10, 20, 50), (40, 60, 160)), ((50, 10, 30), (160, 30, 80)), ((15, 15, 40), (110, 25, 70))],
]

# ---------------- helpers ----------------
def ease_out_back(t):
    t = max(0, min(1, t)); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2

def ease_out(t):
    t = max(0, min(1, t)); return 1 - (1 - t) ** 3

_fc = {}
def font(path, size):
    k = (path, size)
    if k not in _fc: _fc[k] = ImageFont.truetype(path, size)
    return _fc[k]

def parse(line):
    return [(p, YELLOW if i % 2 else WHITE) for i, p in enumerate(line.split("*")) if p]

def text_img(line, path, size, color=None, shadow=True):
    segs = parse(line) if color is None else [(line.replace("*", ""), color)]
    f = font(path, size)
    widths = [f.getlength(s) for s, _ in segs]
    tw = int(sum(widths)) + 1
    asc, desc = f.getmetrics(); pad = 30
    img = Image.new("RGBA", (tw + pad * 2, asc + desc + pad * 2), (0, 0, 0, 0))
    if shadow:
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(sh); x = pad
        for (s, _), w in zip(segs, widths):
            d.text((x + 4, pad + 6), s, font=f, fill=(0, 0, 0, 170)); x += w
        img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(8)))
    d = ImageDraw.Draw(img); x = pad
    for (s, c), w in zip(segs, widths):
        d.text((x, pad), s, font=f, fill=c); x += w
    return img

def fit_size(text, path, size, maxw):
    while font(path, size).getlength(text.replace("*", "")) > maxw and size > 40: size -= 4
    return size

def pill(text, size=40, fg=(20, 20, 20), bg=YELLOW):
    f = font(F_BLACK, size)
    tw = int(f.getlength(text)); asc, desc = f.getmetrics()
    pw, ph = tw + 70, asc + desc + 34
    img = Image.new("RGBA", (pw + 20, ph + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((10, 10, 10 + pw, 10 + ph), radius=ph // 2, fill=bg)
    d.text((10 + 35, 10 + 17), text, font=f, fill=fg)
    return img

def bell_button(text, size=58):
    """Botón rojo de suscripción con una campana dibujada."""
    f = font(F_BLACK, size)
    tw = int(f.getlength(text)); asc, desc = f.getmetrics()
    bw = 70
    pw, ph = tw + bw + 100, asc + desc + 44
    img = Image.new("RGBA", (pw + 30, ph + 30), (0, 0, 0, 0))
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((15, 21, 15 + pw, 21 + ph), radius=ph // 2, fill=(0, 0, 0, 140))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(8)))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((15, 15, 15 + pw, 15 + ph), radius=ph // 2, fill=RED)
    bx, by = 15 + 45, 15 + ph // 2
    d.pieslice((bx - 26, by - 34, bx + 26, by + 18), 180, 360, fill=WHITE)
    d.rectangle((bx - 26, by - 8, bx + 26, by + 14), fill=WHITE)
    d.polygon([(bx - 34, by + 18), (bx + 34, by + 18), (bx + 26, by + 6), (bx - 26, by + 6)], fill=WHITE)
    d.ellipse((bx - 9, by + 18, bx + 9, by + 34), fill=WHITE)
    d.text((15 + 45 + bw, 15 + 22), text, font=f, fill=WHITE)
    return img

def gradient(c1, c2):
    y = np.linspace(0, 1, H)[:, None]; x = np.linspace(0, 1, W)[None, :]
    t = np.clip(0.75 * y + 0.25 * x, 0, 1)[..., None]
    return (np.array(c1)[None, None, :] * (1 - t) + np.array(c2)[None, None, :] * t).astype(np.float32)

def blob(r, color):
    yy, xx = np.mgrid[-r:r, -r:r]
    a = np.clip(1 - np.sqrt(xx ** 2 + yy ** 2) / r, 0, 1) ** 2
    img = np.zeros((2 * r, 2 * r, 4), np.uint8); img[..., :3] = color; img[..., 3] = (a * 70).astype(np.uint8)
    return Image.fromarray(img, "RGBA")

def paste_scaled(canvas, img, cx, cy, scale, alpha, dy=0):
    if alpha <= 0.01 or scale <= 0.02: return
    w, h = img.size
    nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
    im = img.resize((nw, nh), Image.BICUBIC) if (nw, nh) != (w, h) else img
    if alpha < 1:
        a = im.getchannel("A").point(lambda v: int(v * alpha)); im = im.copy(); im.putalpha(a)
    canvas.alpha_composite(im, (int(cx - nw / 2), int(cy - nh / 2 + dy)))

def pop(canvas, img, cx, cy, lt, start, exit_a, dur=0.35):
    p = (lt - start) / dur
    if p > 0: paste_scaled(canvas, img, cx, cy, 0.4 + 0.6 * ease_out_back(p), min(1, p * 2.5) * exit_a)

def slide(canvas, img, cx, cy, lt, start, exit_a, dur=0.3):
    p = (lt - start) / dur
    if p > 0: paste_scaled(canvas, img, cx, cy, 1, min(1, p * 2) * exit_a, dy=(1 - ease_out(p)) * 60)

# ---------------- vídeo ----------------
class Video:
    def __init__(self, g):
        assert len(g["datos"]) == 4, "El guion necesita exactamente 4 datos"
        pal = PALETAS[int(g.get("paleta", 0)) % len(PALETAS)]
        # Voz grabada (voz/intro.wav y voz/outro.wav): alarga gancho y cierre para que quepa
        self.voz = {k: load_wav(os.path.join(AQUI, "voz", f"{k}.wav")) for k in ("intro", "outro")}
        hook_d = max(3.0, len(self.voz["intro"]) / SR + 0.5) if self.voz["intro"] is not None else 3.0
        cta_d = max(3.0, len(self.voz["outro"]) / SR + 0.7) if self.voz["outro"] is not None else 3.0
        t = [0.0, hook_d]
        for _ in range(4): t.append(t[-1] + 3.4)
        t.append(t[-1] + cta_d)
        self.scenes = [dict(kind="hook", t0=t[0], t1=t[1], bg=pal[0])]
        for i, dato in enumerate(g["datos"]):
            s = dict(kind="fact", t0=t[i + 1], t1=t[i + 2], n=i + 1, bg=pal[i + 1])
            s["pill"] = pill(f"CURIOSIDAD {i + 1}/4")
            s["big_size"] = fit_size(dato["grande"], F_BLACK, 300, MAXW)
            s["big_img"] = text_img(dato["grande"], F_BLACK, s["big_size"], YELLOW)
            if dato.get("contar"): s["count"] = tuple(dato["contar"])
            s["line_imgs"] = [text_img(l, F_BOLD, fit_size(l, F_BOLD, 76, MAXW)) for l in dato["lineas"][:3]]
            self.scenes.append(s)
        self.scenes.append(dict(kind="cta", t0=t[5], t1=t[6], bg=pal[5]))
        self.dur = t[-1]
        self.bgs = [gradient(*s["bg"]) for s in self.scenes]
        self.blobs = [blob(420, (255, 255, 255)), blob(330, YELLOW), blob(380, (255, 120, 200))]
        gancho = g.get("gancho", ["4 curiosidades del mundo", "que te van a *sorprender*"])
        self.hook = dict(
            a=text_img("¿SABÍAS", F_BLACK, 210, WHITE), b=text_img("ESTO?", F_BLACK, 250, YELLOW),
            l1=text_img(gancho[0], F_BOLD, fit_size(gancho[0], F_BOLD, 72, MAXW)),
            l2=text_img(gancho[1], F_BOLD, fit_size(gancho[1], F_BOLD, 72, MAXW)),
            p=pill(g.get("pista", "LA ÚLTIMA ES INCREÍBLE"), 40))
        self.cta = dict(
            a=text_img("¿Te ha gustado?", F_BLACK, fit_size("¿Te ha gustado?", F_BLACK, 120, MAXW)),
            l1=text_img("Suscríbete a *Mundo Curioso 5000*", F_BOLD, fit_size("Suscríbete a Mundo Curioso 5000", F_BOLD, 64, MAXW)),
            l2=text_img("3 curiosidades nuevas *cada día*", F_BOLD, fit_size("3 curiosidades nuevas cada día", F_BOLD, 58, MAXW)),
            btn=bell_button("SUSCRÍBETE"))
        self.brand = text_img(CANAL, F_BLACK, 34, (255, 255, 255), shadow=True)
        self.brand.putalpha(self.brand.getchannel("A").point(lambda v: int(v * 0.85)))

    def render(self, fi):
        t = fi / FPS
        si = next(i for i, s in enumerate(self.scenes) if s["t0"] <= t < s["t1"] or i == len(self.scenes) - 1)
        s = self.scenes[si]; lt = t - s["t0"]; sd = s["t1"] - s["t0"]
        bg = self.bgs[si]
        if si > 0 and lt < 0.3:
            k = ease_out(lt / 0.3); bg = self.bgs[si - 1] * (1 - k) + bg * k
        canvas = Image.fromarray(bg.astype(np.uint8), "RGB").convert("RGBA")
        for j, b in enumerate(self.blobs):
            bx = W * (0.5 + 0.42 * math.sin(t * (0.35 + 0.17 * j) + j * 2.1))
            by = H * (0.5 + 0.38 * math.cos(t * (0.28 + 0.11 * j) + j * 1.3))
            canvas.alpha_composite(b, (int(bx - b.width / 2), int(by - b.height / 2)))
        exit_a = 1.0 if s is self.scenes[-1] else min(1, max(0, (sd - lt) / 0.18))

        if s["kind"] == "hook":
            h = self.hook
            shake = 8 * math.sin(lt * 60) * max(0, 1 - lt / 0.4)
            pop(canvas, h["a"], CX + shake, 670, lt, 0.0, exit_a)
            pop(canvas, h["b"], CX - shake, 925, lt, 0.18, exit_a)
            slide(canvas, h["l1"], CX, 1110, lt, 0.6, exit_a)
            slide(canvas, h["l2"], CX, 1205, lt, 0.75, exit_a)
            pulse = 1 + 0.05 * math.sin(lt * 12) if lt > 1.8 else 1
            p = (lt - 1.4) / 0.35
            if p > 0: paste_scaled(canvas, h["p"], CX, 1370, (0.4 + 0.6 * ease_out_back(p)) * pulse, min(1, p * 2.5) * exit_a)
        elif s["kind"] == "fact":
            pop(canvas, s["pill"], CX, 560, lt, 0.05, exit_a)
            img = s["big_img"]
            if "count" in s:
                a, b, fmt = s["count"]
                k = ease_out(min(1, (lt - 0.15) / 0.8))
                v = int(round(a + (b - a) * k))
                if v != b: img = text_img(fmt.format(f"{v:,}".replace(",", ".")), F_BLACK, s["big_size"], YELLOW)
            pop(canvas, img, CX, 790, lt, 0.15, exit_a, dur=0.4)
            for i, li in enumerate(s["line_imgs"]):
                slide(canvas, li, CX, 1010 + i * 100, lt, 0.55 + i * 0.32, exit_a)
        else:
            c = self.cta
            pop(canvas, c["a"], CX, 640, lt, 0.05, exit_a)
            slide(canvas, c["l1"], CX, 790, lt, 0.35, exit_a)
            slide(canvas, c["l2"], CX, 880, lt, 0.55, exit_a)
            p = (lt - 0.75) / 0.35
            if p > 0:
                pulse = 1 + 0.06 * math.sin((lt - 0.75) * 9)
                paste_scaled(canvas, c["btn"], CX, 1080, (0.4 + 0.6 * ease_out_back(p)) * pulse, min(1, p * 2.5))
            # "toque" animado sobre el botón
            if lt > 1.3:
                q = ((lt - 1.3) % 1.0)
                d = ImageDraw.Draw(canvas)
                r = 30 + 90 * q; al = int(200 * (1 - q))
                tx = CX + c["btn"].width // 2 - 25; ty = 1080 + c["btn"].height // 2 - 5
                d.ellipse((tx - r, ty - r, tx + r, ty + r), outline=(255, 255, 255, al), width=8)
                d.ellipse((tx - 15, ty - 15, tx + 15, ty + 15), fill=(255, 255, 255, 230))

        d = ImageDraw.Draw(canvas)
        d.rounded_rectangle((60, 250, W - 60, 262), radius=6, fill=(255, 255, 255, 70))
        d.rounded_rectangle((60, 250, 60 + int((W - 120) * t / self.dur), 262), radius=6, fill=YELLOW)
        canvas.alpha_composite(self.brand, (int(CX - self.brand.width / 2), 285))
        return canvas.convert("RGB")

# ---------------- audio ----------------
def make_audio(path, video, seed=1):
    SR = 44100; dur = video.dur
    n = int(dur * SR); out = np.zeros(n); tt = np.arange(n) / SR
    rng = np.random.default_rng(seed)
    bpm = 120 + (seed % 3) * 4; beat = 60 / bpm
    def add(sig, at):
        i = int(at * SR); j = min(n, i + len(sig))
        if 0 <= i < n: out[i:j] += sig[: j - i]
    kl = int(0.35 * SR); kt = np.arange(kl) / SR
    kick = np.sin(2 * np.pi * np.cumsum(45 + 90 * np.exp(-kt * 25)) / SR) * np.exp(-kt * 9)
    hl = int(0.06 * SR); hat = np.diff(rng.standard_normal(hl + 1)) * np.exp(-np.arange(hl) / SR * 70) * 0.18
    cl = int(0.18 * SR); clap = rng.standard_normal(cl) * np.exp(-np.arange(cl) / SR * 22) * 0.25
    for b in range(int(dur / beat) + 1):
        at = b * beat
        if at > dur - 0.6: break
        add(kick * 0.9, at); add(hat, at + beat / 2)
        if b % 2 == 1: add(clap, at)
    progs = [[110.0, 87.31, 130.81, 98.0], [98.0, 130.81, 87.31, 110.0], [116.54, 92.5, 138.59, 103.83]]
    roots = progs[seed % len(progs)]; bar = beat * 4
    for k in range(int(dur / bar) + 1):
        f0 = roots[k % 4]; i0 = int(k * bar * SR); i1 = min(n, int((k + 1) * bar * SR))
        seg = tt[i0:i1] - k * bar
        out[i0:i1] += 0.22 * np.sin(2 * np.pi * f0 * seg) * np.minimum(1, seg * 20) * np.exp(-(seg % beat) * 3)
        out[i0:i1] += 0.05 * sum(np.sin(2 * np.pi * f0 * m * 2 * seg) for m in (1, 1.2, 1.5)) / 3 * np.minimum(1, seg * 4)
    wl = int(0.35 * SR); wt = np.arange(wl) / SR
    whoosh = np.convolve(rng.standard_normal(wl), np.ones(12) / 12, mode="same") * (wt / 0.35) ** 2 * 0.6
    il = int(0.5 * SR); it = np.arange(il) / SR
    impact = np.sin(2 * np.pi * (40 + 60 * np.exp(-it * 15)) * it) * np.exp(-it * 6) * 0.8
    for s in video.scenes[1:]:
        add(whoosh, s["t0"] - 0.35); add(impact, s["t0"])
    add(impact, 0.0)
    bl = int(0.12 * SR); bt = np.arange(bl) / SR
    blip = np.sin(2 * np.pi * 1320 * bt) * np.exp(-bt * 30) * 0.15
    for s in video.scenes:
        if s["kind"] == "fact": add(blip, s["t0"] + 0.2)
    add(blip * 1.4, video.scenes[-1]["t0"] + 0.8)   # botón de suscripción
    music = np.tanh(out * 1.2); music /= np.max(np.abs(music)) * 1.12

    # Voz: intro al empezar el gancho, outro al empezar el cierre; la música baja mientras se habla
    voice = np.zeros(n); duck = np.zeros(n)
    for clip, at in ((video.voz.get("intro"), 0.25), (video.voz.get("outro"), video.scenes[-1]["t0"] + 0.35)):
        if clip is None: continue
        i = int(at * SR); j = min(n, i + len(clip))
        voice[i:j] += clip[: j - i]
        duck[max(0, i - int(0.15 * SR)):min(n, j + int(0.25 * SR))] = 1.0
    if voice.any():
        k = int(0.12 * SR); duck = np.convolve(duck, np.ones(k) / k, mode="same")   # transiciones suaves
        music_gain = 0.6 - 0.42 * np.clip(duck, 0, 1)
        out = music * music_gain + voice * 0.95
    else:
        out = music * 0.9
    fo = int(0.6 * SR); out[-fo:] *= np.linspace(1, 0, fo)
    out = np.clip(out, -0.98, 0.98)
    pcm = (out * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(np.stack([pcm, pcm], axis=1).tobytes())

def main():
    if len(sys.argv) < 2: raise SystemExit(__doc__)
    guion_path = sys.argv[1]
    g = json.load(open(guion_path, encoding="utf-8"))
    v = Video(g)
    out_dir = os.path.join(AQUI, "videos"); os.makedirs(out_dir, exist_ok=True)
    if "--preview" in sys.argv:
        prev = os.path.join(tempfile.gettempdir(), f"preview_{g['id']}")
        os.makedirs(prev, exist_ok=True)
        frames = [v.render(int(sec * FPS)).resize((360, 640)) for sec in [sc['t0'] + 0.8 * (sc['t1'] - sc['t0']) for sc in v.scenes]]
        sheet = Image.new("RGB", (360 * 6, 640))
        for i, f in enumerate(frames): sheet.paste(f, (i * 360, 0))
        sheet.save(os.path.join(prev, "hoja.png")); print(os.path.join(prev, "hoja.png")); return
    seed = sum(map(ord, g["id"]))
    wav = os.path.join(tempfile.gettempdir(), f"audio_{g['id']}.wav"); make_audio(wav, v, seed)
    out = os.path.join(out_dir, f"{g['id']}.mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", wav,
                          "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
                          "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out],
                         stdin=subprocess.PIPE)
    for fi in range(int(v.dur * FPS)):
        p.stdin.write(v.render(fi).tobytes())
    p.stdin.close(); p.wait()
    if p.returncode != 0: raise SystemExit("ffmpeg falló")
    print(out)

if __name__ == "__main__":
    main()
