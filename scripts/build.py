#!/usr/bin/env python3
"""Regenerates assets/*.svg for the profile README.

Edit the text constants or STACK below, then run:  python3 scripts/build.py
"""
import base64
import hashlib
import html
import re
import subprocess
import urllib.parse
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
CACHE = Path(__file__).resolve().parent / ".cache"

NAME = "RAHUL L S"
CASE_NO = "8283"
EPIGRAPH = "There’s no such thing as magic. Only systems, read closely."
ROLES = ["FULL-STACK", "CROSS-PLATFORM", "AI SYSTEMS"]

FILE = [
    ("SUBJECT", "Rahul L S"),
    ("ALIAS", "rahul-ls  /  Rahul-8283"),
    ("LAST SEEN", "Erode, Tamil Nadu"),
    ("STATUS", "building, breaking, becoming"),
]
READING = [
    ("Thirty-eight tools. Ten of them are databases.",
     "No favourites, only a question: what must this remember?"),
    ("Web, mobile, desktop. Same pair of hands.",
     "The screen is incidental. He builds what sits behind it."),
    ("LangGraph. Retrieval. A voice that picks up the phone.",
     "He never trusts a model alone. He gives it memory, and a way back."),
]
MARGIN_NOTE = "you were going to scroll down anyway."

LEADS = [
    ("portfolio", "Portfolio", "https://rahul-ls-ai.vercel.app/"),
    ("linkedin", "LinkedIn", "https://www.linkedin.com/in/rahul-ls"),
    ("email", "Email", "mailto:lsrahul12@gmail.com"),
    ("instagram", "Instagram", "https://www.instagram.com/rahul._ls_/"),
]

# Icon ids come from skillicons.dev unless listed in SIMPLE or CUSTOM.
STACK = [
    ("Languages", ["cpp", "py", "js", "ts", "dart"]),
    ("Client-Side", ["react", "nextjs", "tailwind", "flutter", "tauri", "html", "css"]),
    ("Server-Side", ["nodejs", "express", "fastapi", "flask"]),
    ("Databases", ["postgres", "mongodb", "redis", "neo4j", "pinecone", "chroma",
                   "pgvector", "turso", "supabase", "firebase"]),
    ("AI-ML", ["sklearn", "pytorch", "tensorflow", "langchain", "langgraph"]),
    ("Tools", ["git", "github", "postman", "cloudinary", "twilio", "docker", "aws"]),
]

# simple-icons slug -> glyph colour, drawn on a skillicons-style dark tile.
SIMPLE = {
    "neo4j": "#5B9BD5",
    "turso": "#4FF8D2",
    "langchain": "#FFFFFF",
    "langgraph": "#FFFFFF",
    "cloudinary": "#6C7FF2",
    "twilio": "#F22F46",
}

# Brands with no icon in either set, drawn by hand on a 256 box.
CUSTOM = {
    "pinecone": (
        '<g fill="none" stroke="#fff" stroke-width="13" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M128 52v152"/><path d="M104 84l24-24 24 24"/>'
        '<path d="M88 132l40-34 40 34"/><path d="M96 178l32-30 32 30"/>'
        '<path d="M70 104l-14-6M186 104l14-6M62 156l-16 2M194 156l16 2"/></g>'
    ),
    "chroma": (
        '<clipPath id="lens"><circle cx="104" cy="128" r="54"/></clipPath>'
        '<circle cx="104" cy="128" r="54" fill="#327EFF"/>'
        '<circle cx="152" cy="128" r="54" fill="#FFDE2D"/>'
        '<circle cx="152" cy="128" r="54" fill="#FF6446" clip-path="url(#lens)"/>'
    ),
    "pgvector": (
        '<g fill="none" stroke-width="13" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M86 66H62v124h24M170 66h24v124h-24" stroke="#fff"/>'
        '<path d="M98 158l58-58M124 98h34v34" stroke="#6EA8DC"/></g>'
    ),
}

NIGHT = "#0e0d0c"
CREAM = "#ece4d2"
INK = "#2a241e"
FADED = "#6e6457"
RED = "#a3261c"
GOLD = "#b39a68"

# family alias -> (Google Fonts css2 family spec, fallback stack)
FONTS = {
    "serif": ("Cormorant+Garamond:ital,wght@0,500;0,600;1,500", "Georgia,'Times New Roman',serif"),
    "type": ("Courier+Prime:wght@400;700", "'Courier New',Courier,monospace"),
    "hand": ("Caveat:wght@500", "'Bradley Hand','Segoe Print',cursive"),
}
USED = defaultdict(set)


def esc(s):
    return html.escape(s, quote=False)


def text(x, y, s, font, size, fill, **attrs):
    USED[font].update(s)
    extra = "".join(f' {k.rstrip("_").replace("_", "-")}="{v}"' for k, v in attrs.items())
    return f'<text x="{x}" y="{y}" class="{font}" font-size="{size}" fill="{fill}"{extra}>{esc(s)}</text>'


def fetch(url, path, binary=False):
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["curl", "-fsSL", "-A", "Mozilla/5.0", url, "-o", str(path)], check=True)
    return path.read_bytes() if binary else path.read_text()


def font_css():
    """@font-face rules with each family subset to exactly the glyphs this SVG uses."""
    rules = []
    for alias, chars in USED.items():
        spec, fallback = FONTS[alias]
        glyphs = "".join(sorted(chars | set(" ")))
        url = (f"https://fonts.googleapis.com/css2?family={spec}"
               f"&text={urllib.parse.quote(glyphs)}")
        key = hashlib.sha1(url.encode()).hexdigest()[:16]
        css = fetch(url, CACHE / f"font-{key}.css")
        for block in re.findall(r"@font-face\s*{([^}]*)}", css):
            style = re.search(r"font-style:\s*(\w+)", block).group(1)
            weight = re.search(r"font-weight:\s*(\d+)", block).group(1)
            src = re.search(r"url\(([^)]+)\)", block).group(1)
            data = fetch(src, CACHE / f"font-{hashlib.sha1(src.encode()).hexdigest()[:16]}.ttf", binary=True)
            rules.append(f"@font-face{{font-family:'{alias}-x';font-style:{style};font-weight:{weight};"
                         f"src:url(data:font/ttf;base64,{base64.b64encode(data).decode()}) format('truetype')}}")
        rules.append(f".{alias}{{font-family:'{alias}-x',{fallback}}}")
    USED.clear()
    return "".join(rules)


def svg(w, h, label, body, defs="", css=""):
    fonts = font_css()
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'role="img" aria-label="{html.escape(label)}">\n<style>{fonts}{css}</style>\n'
            f'<defs>{defs}</defs>\n{body}\n</svg>\n')


GRAIN = ('<filter id="grain" x="0" y="0" width="100%" height="100%">'
         '<feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" stitchTiles="stitch"/>'
         '<feColorMatrix values="0 0 0 0 1  0 0 0 0 .95  0 0 0 0 .88  0 0 0 .09 0"/></filter>')
ROUGH = ('<filter id="rough" x="-10%" y="-10%" width="120%" height="120%">'
         '<feTurbulence type="fractalNoise" baseFrequency=".06" numOctaves="2" seed="7"/>'
         '<feDisplacementMap in="SourceGraphic" scale="3.2"/></filter>')
PAPER = ('<filter id="mottle" x="0" y="0" width="100%" height="100%">'
         '<feTurbulence type="fractalNoise" baseFrequency=".022 .035" numOctaves="4" seed="3"/>'
         '<feColorMatrix values="0 0 0 0 .45  0 0 0 0 .33  0 0 0 0 .2  0 0 0 .55 -.18"/></filter>'
         '<filter id="fibre" x="0" y="0" width="100%" height="100%">'
         '<feTurbulence type="fractalNoise" baseFrequency="1.4" numOctaves="1" seed="5"/>'
         '<feColorMatrix values="0 0 0 0 .3  0 0 0 0 .24  0 0 0 0 .16  0 0 0 .22 0"/></filter>'
         '<filter id="lift" x="-10%" y="-10%" width="120%" height="130%"><feGaussianBlur stdDeviation="10"/></filter>')
EDGE = ('<radialGradient id="edge" cx=".5" cy=".45" r=".75">'
        '<stop offset=".6" stop-color="#7a5a32" stop-opacity="0"/>'
        '<stop offset="1" stop-color="#7a5a32" stop-opacity=".28"/></radialGradient>')


def paper(pid, x, y, w, h, base=CREAM, rx=2):
    """A sheet: base colour, mottling, fibre, darker edges, drop shadow."""
    return (
        f'<rect x="{x + 4}" y="{y + 12}" width="{w - 8}" height="{h}" fill="#000" opacity=".55" filter="url(#lift)"/>'
        f'<clipPath id="{pid}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}"/></clipPath>'
        f'<g clip-path="url(#{pid})"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{base}"/>'
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" filter="url(#mottle)" opacity=".5"/>'
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" filter="url(#fibre)"/>'
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#edge)"/></g>'
    )


# ---------------------------------------------------------------- icons

def scope(s, prefix):
    for i in set(re.findall(r'\bid="([^"]+)"', s)):
        s = (s.replace(f'id="{i}"', f'id="{prefix}-{i}"')
              .replace(f"url(#{i})", f"url(#{prefix}-{i})")
              .replace(f'href="#{i}"', f'href="#{prefix}-{i}"'))
    return s


def tile(body):
    return f'<rect width="256" height="256" rx="60" fill="#242938"/>{body}'


def icon(name, x, y, size):
    if name in CUSTOM:
        body = tile(CUSTOM[name])
    elif name in SIMPLE:
        raw = fetch(f"https://cdn.jsdelivr.net/npm/simple-icons@latest/icons/{name}.svg",
                    CACHE / f"simple-{name}.svg")
        d = re.search(r'<path d="([^"]+)"', raw).group(1)
        body = tile(f'<path transform="translate(56 56) scale(6)" fill="{SIMPLE[name]}" d="{d}"/>')
    else:
        raw = fetch(f"https://skillicons.dev/icons?i={name}&theme=dark", CACHE / f"skill-{name}.svg")
        body = re.search(r"<g[^>]*>\s*<svg[^>]*>(.*)</svg>\s*</g>", raw, re.S).group(1)
    return (f'<svg x="{x}" y="{y}" width="{size}" height="{size}" viewBox="0 0 256 256" fill="none">'
            f"{scope(body, name)}</svg>")


# ---------------------------------------------------------------- the file

SMILEY = ('<g class="draw" fill="none" stroke="{c}" stroke-linecap="round" stroke-linejoin="round" filter="url(#rough)">'
          '<path pathLength="1" stroke-width="5.5" d="M52 9C77 8 93 28 92 52 91 77 72 93 48 92 24 91 8 73 9 49 10 26 28 10 55 10"/>'
          '<path pathLength="1" stroke-width="6" d="M36 33l-1 14"/><path pathLength="1" stroke-width="6" d="M64 32v14"/>'
          '<path pathLength="1" stroke-width="5.5" d="M26 59c9 18 38 20 48 1"/>'
          '<path pathLength="1" stroke-width="4" d="M43 92l1 13"/></g>')


def stamp(cx, cy):
    ring = f"CASE No. {CASE_NO}  ·  STILL OPEN  ·  "
    USED["type"].update(ring + "OPEN")
    return (
        f'<g transform="rotate(-14 {cx} {cy})" opacity=".78" filter="url(#rough)">'
        f'<path id="ring" d="M{cx - 33} {cy}a33 33 0 1 1 66 0a33 33 0 1 1 -66 0" fill="none"/>'
        f'<circle cx="{cx}" cy="{cy}" r="44" fill="none" stroke="{RED}" stroke-width="2.6"/>'
        f'<circle cx="{cx}" cy="{cy}" r="25" fill="none" stroke="{RED}" stroke-width="1.4"/>'
        f'<text class="type" font-size="7.8" font-weight="700" fill="{RED}" letter-spacing="1">'
        f'<textPath href="#ring">{esc(ring)}</textPath></text>'
        f'<text x="{cx}" y="{cy + 5}" class="type" font-size="13" font-weight="700" fill="{RED}" '
        f'text-anchor="middle" letter-spacing="1">OPEN</text></g>'
    )


def dossier():
    W, H = 880, 930
    px, py, pw, ph = 112, 352, 656, 494
    body = [
        f'<rect width="{W}" height="{H}" rx="14" fill="{NIGHT}"/>',
        f'<rect width="{W}" height="{H}" rx="14" fill="url(#lamp)"/>',
        f'<rect width="{W}" height="{H}" rx="14" filter="url(#grain)"/>',
        f'<rect x="18.5" y="18.5" width="{W - 37}" height="{H - 37}" rx="6" fill="none" stroke="{GOLD}" stroke-opacity=".35"/>',
        f'<rect x="24.5" y="24.5" width="{W - 49}" height="{H - 49}" rx="4" fill="none" stroke="{GOLD}" stroke-opacity=".18"/>',
        '<g>'
        f'<path d="M262 82h110M508 82h110" stroke="{GOLD}" stroke-opacity=".55"/>'
        + text(W / 2, 86.5, f"CASE FILE No. {CASE_NO}", "type", 12, GOLD, text_anchor="middle", letter_spacing="3")
        + '</g>',
        '<g>'
        + text(W / 2 + 7, 178, NAME, "serif", 84, "#efe7d6", font_weight="600", text_anchor="middle",
               letter_spacing="14")
        + '</g>',
        '<g>'
        + text(W / 2, 226, EPIGRAPH, "serif", 23, "#b9ae99", font_style="italic", text_anchor="middle")
        + '</g>',
        '<g>'
        + text(W / 2, 282, "    ·    ".join(ROLES), "type", 11.5, "#8f8676", text_anchor="middle",
               letter_spacing="3.2")
        + '</g>',
        f'<g transform="translate(790 846) scale(.4)">{SMILEY.format(c=RED)}</g>',
    ]

    sheet = [paper("sheet", px, py, pw, ph)]
    sheet.append(f'<g filter="url(#rough)" fill="none" stroke="#7b5326">'
                 f'<circle cx="{px + pw - 120}" cy="{py + ph - 70}" r="47" stroke-width="3.5" opacity=".16"/>'
                 f'<circle cx="{px + pw - 116}" cy="{py + ph - 66}" r="44" stroke-width="1.2" opacity=".12"/></g>')
    sheet.append(f'<path d="M{px + 40} {py + 46}V{py - 14}a10 10 0 0 1 20 0V{py + 40}a6 6 0 0 1 -12 0V{py - 6}" '
                 f'fill="none" stroke="url(#steel)" stroke-width="2.6" stroke-linecap="round"/>')
    tx = px + 52
    y = py + 60
    for label, value in FILE:
        dots = "." * (14 - len(label))
        sheet.append(text(tx, y, f"{label} {dots}", "type", 13, FADED))
        sheet.append(text(tx + 128, y, value, "type", 13.5, INK, font_weight="700" if label == "SUBJECT" else "400"))
        y += 23
    sheet.append(stamp(px + pw - 92, py + 78))
    y += 18
    sheet.append(f'<path d="M{tx} {y}h{pw - 104}" stroke="{INK}" stroke-opacity=".35" stroke-dasharray="2 3"/>')
    y += 38
    sheet.append(text(tx, y, "THE READING", "type", 13, INK, font_weight="700", letter_spacing="4"))
    sheet.append(text(tx + 150, y, "what he gives away without saying", "serif", 17, FADED, font_style="italic"))
    y += 40
    for n, (obs, inf) in enumerate(READING):
        sheet.append(text(tx, y, ["I.", "II.", "III."][n], "serif", 17, RED, font_weight="600"))
        sheet.append(text(tx + 36, y, obs, "type", 12.5, FADED))
        sheet.append(text(tx + 36, y + 26, inf, "serif", 20.5, INK, font_style="italic", font_weight="500"))
        y += 66
    note_x, note_y = px + pw - 316, py + ph - 24
    sheet.append(f'<g transform="rotate(-3 {note_x} {note_y})">'
                 + text(note_x, note_y, MARGIN_NOTE, "hand", 23, RED, opacity=".88")
                 + f'<path d="M{note_x + 262} {note_y - 16}c14 10 16 26 6 40m0 0l-2-10m2 10l9-5" fill="none" '
                 f'stroke="{RED}" stroke-opacity=".8" stroke-width="1.8" stroke-linecap="round"/></g>')
    body.append(f'<g transform="rotate(-.9 {px + pw / 2} {py + ph / 2})">{"".join(sheet)}</g>')

    defs = (GRAIN + ROUGH + PAPER + EDGE +
            '<radialGradient id="lamp" cx=".5" cy=".18" r=".7">'
            '<stop offset="0" stop-color="#2b2520" stop-opacity=".9"/><stop offset="1" stop-color="#2b2520" stop-opacity="0"/>'
            '</radialGradient>'
            '<linearGradient id="steel" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#d9dcde"/>'
            '<stop offset=".5" stop-color="#8d9296"/><stop offset="1" stop-color="#c7cbce"/></linearGradient>')
    css = ("@keyframes ink{to{stroke-dashoffset:0}}"
           ".draw path{stroke-dasharray:1 2;stroke-dashoffset:1.05;animation:ink 1.1s ease-in-out forwards}"
           ".draw path:nth-child(1){animation-delay:2.2s}"
           ".draw path:nth-child(2){animation-delay:3.1s;animation-duration:.25s}"
           ".draw path:nth-child(3){animation-delay:3.35s;animation-duration:.25s}"
           ".draw path:nth-child(4){animation-delay:3.65s;animation-duration:.6s}"
           ".draw path:nth-child(5){animation-delay:4.2s;animation-duration:.9s}"
           "@media (prefers-reduced-motion:reduce){.draw path{animation:none;stroke-dashoffset:0}}")
    label = f"Case file No. {CASE_NO}: Rahul L S. Full-stack, cross-platform, AI systems. " + " ".join(
        f"{o} {i}" for o, i in READING)
    return svg(W, H, label, "".join(body), defs, css)


# ---------------------------------------------------------------- evidence wall

def pin(x, y):
    return (f'<ellipse cx="{x + 3}" cy="{y + 5}" rx="7" ry="4" fill="#000" opacity=".45"/>'
            f'<circle cx="{x}" cy="{y}" r="7.5" fill="url(#pinhead)"/>'
            f'<circle cx="{x - 2.4}" cy="{y - 2.6}" r="2.2" fill="#fff" opacity=".55"/>')


def evidence():
    W, H = 880, 600
    cw, ch, gap = 250, 168, 32
    x0 = (W - 3 * cw - 2 * gap) / 2
    rows_y = [128, 352]
    tilt = [-2.2, 1.4, -1.1, 1.6, -1.7, 2.1]
    cards, pins = [], []
    for i, (cat, items) in enumerate(STACK):
        x = x0 + (i % 3) * (cw + gap)
        y = rows_y[i // 3]
        cx = x + cw / 2
        c = [paper(f"card{i}", x, y, cw, ch, base="#f1ead9", rx=1.5)]
        c.append(f'<path d="M{x} {y + 46.5}h{cw}" stroke="#c0453b" stroke-opacity=".55"/>')
        c += [f'<path d="M{x} {y + 46.5 + k * 21}h{cw}" stroke="#6f93b8" stroke-opacity=".18"/>' for k in range(1, 6)]
        c.append(text(x + 18, y + 33, f"EXHIBIT {'ABCDEF'[i]}", "type", 10.5, RED, letter_spacing="2", font_weight="700"))
        c.append(text(x + cw - 18, y + 34, cat, "serif", 20, INK, font_style="italic", text_anchor="end"))
        size, step = 34, 43
        for k, name in enumerate(items):
            col, row = k % 5, k // 5
            n_row = min(5, len(items) - row * 5)
            ix = cx - (n_row * step - (step - size)) / 2 + col * step
            c.append(icon(name, round(ix, 1), y + 64 + row * 46, size))
        cards.append(f'<g transform="rotate({tilt[i]} {cx} {y + ch / 2})">{"".join(c)}</g>')
        pins.append((cx, y + 9))

    threads = []
    for a, b in [(0, 1), (1, 2), (0, 4), (1, 5), (2, 3), (3, 4), (4, 5)]:
        (ax, ay), (bx, by) = pins[a], pins[b]
        threads.append(f'<path d="M{ax} {ay}Q{(ax + bx) / 2} {(ay + by) / 2 + 14} {bx} {by}"/>')
    thread_paths = "".join(threads)

    body = [
        f'<rect width="{W}" height="{H}" rx="14" fill="#16130f"/>',
        f'<rect width="{W}" height="{H}" rx="14" fill="url(#wall)"/>',
        f'<rect width="{W}" height="{H}" rx="14" filter="url(#grain)"/>',
        f'<rect x="18.5" y="18.5" width="{W - 37}" height="{H - 37}" rx="6" fill="none" stroke="{GOLD}" stroke-opacity=".3"/>',
        text(W / 2, 64, "EXHIBITS", "type", 12, GOLD, text_anchor="middle", letter_spacing="6"),
        text(W / 2, 92, "everything he carries into a case", "serif", 21, "#b9ae99", font_style="italic",
             text_anchor="middle"),
        f'<g fill="none" stroke="#000" stroke-opacity=".5" stroke-width="2.4" transform="translate(1.5 3)">{thread_paths}</g>',
        f'<g fill="none" stroke="{RED}" stroke-width="1.5">{thread_paths}</g>',
        "".join(cards),
        "".join(pin(x, y) for x, y in pins),
        text(W - 46, H - 40, f"{sum(len(i) for _, i in STACK)} items logged", "type", 10.5, "#6f675b",
             text_anchor="end", letter_spacing="1.5"),
    ]
    defs = (GRAIN + PAPER + EDGE +
            '<radialGradient id="wall" cx=".5" cy=".42" r=".72">'
            '<stop offset="0" stop-color="#2d2620" stop-opacity=".95"/><stop offset="1" stop-color="#0b0a09" stop-opacity=".9"/>'
            '</radialGradient>'
            '<radialGradient id="pinhead" cx=".38" cy=".35" r=".75"><stop offset="0" stop-color="#d4473a"/>'
            '<stop offset=".7" stop-color="#8d1d14"/><stop offset="1" stop-color="#5a0f0a"/></radialGradient>')
    label = "Evidence wall. " + " ".join(f"{c}: {', '.join(i)}." for c, i in STACK)
    return svg(W, H, label, "".join(body), defs)


# ---------------------------------------------------------------- leads

def lead(n, label):
    W, H = 200, 76
    x, y, w, h = 30, 10, 162, 56
    body = (
        f'<path d="M4 {y + h / 2 + 4}C14 {y + h / 2 + 14} 26 {y + h / 2 - 6} {x + 18} {y + h / 2}" fill="none" '
        f'stroke="{RED}" stroke-width="1.6" stroke-linecap="round"/>'
        f'<rect x="{x + 4}" y="{y + 5}" width="{w - 6}" height="{h - 10}" rx="3" fill="#000" opacity=".2" filter="url(#lift)"/>'
        f'<clipPath id="tag"><path d="M{x + 16} {y}H{x + w}V{y + h}H{x + 16}L{x} {y + h - 16}V{y + 16}z"/></clipPath>'
        f'<g clip-path="url(#tag)"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#efe6d3"/>'
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" filter="url(#mottle)" opacity=".45"/>'
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" filter="url(#fibre)"/></g>'
        f'<circle cx="{x + 18}" cy="{y + h / 2}" r="7.5" fill="#c9b892"/>'
        f'<circle cx="{x + 18}" cy="{y + h / 2}" r="3.6" fill="#1a1612"/>'
        f'<path d="M{x + 34} {y + 10}v{h - 20}" stroke="{RED}" stroke-opacity=".5" stroke-dasharray="2 3"/>'
        + text(x + 46, y + 23, f"LEAD {n:02d}", "type", 9.5, RED, letter_spacing="2", font_weight="700")
        + text(x + 46, y + 45, label, "serif", 22, INK, font_weight="600")
    )
    return svg(W, H, label, body, PAPER)


def main():
    ASSETS.mkdir(exist_ok=True)
    for old in ASSETS.glob("*.svg"):
        old.unlink()
    files = {"dossier.svg": dossier(), "evidence.svg": evidence()}
    for n, (slug, label, _) in enumerate(LEADS, 1):
        files[f"lead-{slug}.svg"] = lead(n, label)
    for name, content in files.items():
        (ASSETS / name).write_text(content)
        print(f"{name:22} {len(content) / 1024:6.1f} KB")


if __name__ == "__main__":
    main()
