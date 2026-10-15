#!/usr/bin/env python3
"""Regenerates assets/*.svg for the profile README.

Edit the text constants or STACK below, then run:  python3 scripts/build.py
"""
import base64
import math
import hashlib
import html
import re
import random
import subprocess
import textwrap
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
    ("STATUS", "building, breaking, becoming"),
    ("REVIEWED BY", "P. Jane, consultant"),
]
READING = [
    ("Reads the logs before he touches the code.",
     "He reads code like I read a room. The tell is never where it points."),
    ("Web, mobile, desktop. Same pair of hands.",
     "The screen is incidental. He builds what sits behind it."),
    ("LangGraph. Retrieval. A voice that picks up the phone.",
     "He never trusts a model alone. He gives it memory, and a way back."),
]
MARGIN_NOTE = "you were going to scroll down anyway.  — PJ"

CLIPPING = {
    "headline": "Multilingual voice agent takes third worldwide",
    "deck": ["Sambhaash AI, a multilingual sales-call agent, places in the Sarvam AI track",
             "and among the fifty best projects of the Namespace Hackathon."],
    "columns": [
        ("3RD PLACE  ·  SARVAM AI TRACK",
         "Awarded $200 in Sarvam AI credits for a high-fidelity conversational agent built on Bulbul v3."),
        ("TOP 50  ·  OVERALL",
         "Recognised as a top-50 project worldwide, with a $20 cash prize for the Work, Finance & Digital Economy theme."),
    ],
}

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
          '<path pathLength="1" stroke-width="4" d="M43 92l1 13"/>'
          '<path pathLength="1" stroke-width="3.2" d="M66 86l1 22"/>'
          '<path pathLength="1" stroke-width="3" d="M27 76l-1 17"/></g>')
SPATTER = [(104, 30, 2.6), (112, 44, 1.6), (-8, 64, 2.2), (98, 88, 1.4), (118, 22, 1.2), (-14, 40, 1.3)]


def red_john(x, y, scale, colour="#7a140e"):
    """The smiley as painted on a wall: face, eyes, grin and runs of blood."""
    drips = [(30, 80, 34, 3.4), (50, 93, 44, 3.8), (71, 82, 24, 3.1), (40, 91, 16, 2.6)]
    runs = "".join(f'<path d="M{dx} {dy}c.4 {ln * .4} -.6 {ln * .7} 0 {ln}" stroke-width="{r * .9:.1f}"/>'
                   f'<circle cx="{dx}" cy="{dy + ln + .5}" r="{r}" stroke="none" fill="{colour}"/>'
                   for dx, dy, ln, r in drips)
    dots = "".join(f'<circle cx="{a}" cy="{b}" r="{r}" stroke="none" fill="{colour}"/>' for a, b, r in SPATTER)
    return (f'<g transform="translate({x} {y}) scale({scale})" fill="none" stroke="{colour}" stroke-linecap="round" '
            f'stroke-linejoin="round" filter="url(#rough)" opacity=".9">'
            '<path stroke-width="7" d="M52 9C77 8 93 28 92 52 91 77 72 93 48 92 24 91 8 73 9 49 10 26 28 10 55 10"/>'
            '<path stroke-width="8" d="M36 32l-1 16"/><path stroke-width="8" d="M64 31v16"/>'
            f'<path stroke-width="7" d="M25 58c9 19 40 21 50 1"/>{runs}{dots}</g>')


def fingerprint(cx, cy, seed=21):
    rng = random.Random(seed)
    rings = []
    for i in range(1, 11):
        rx, ry = 2 + i * 2.5, 3 + i * 3.2
        dash = " ".join(f"{rng.uniform(4, 22):.1f} {rng.uniform(1.5, 5):.1f}" for _ in range(4))
        rings.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" stroke-dasharray="{dash}" '
                     f'stroke-dashoffset="{rng.uniform(0, 30):.1f}"/>')
    return (f'<g transform="rotate(24 {cx} {cy})" fill="none" stroke="#7d2116" stroke-width="1.5" '
            f'opacity=".4" filter="url(#rough)">{"".join(rings)}</g>')


def stamp(cx, cy):
    ring = f"C.B.I.  ·  CASE No. {CASE_NO}  ·  STILL OPEN  ·  "
    USED["type"].update(ring + "OPEN")
    return (
        f'<g transform="rotate(-14 {cx} {cy})" opacity=".78" filter="url(#rough)">'
        f'<path id="ring" d="M{cx - 33} {cy}a33 33 0 1 1 66 0a33 33 0 1 1 -66 0" fill="none"/>'
        f'<circle cx="{cx}" cy="{cy}" r="44" fill="none" stroke="{RED}" stroke-width="2.6"/>'
        f'<circle cx="{cx}" cy="{cy}" r="25" fill="none" stroke="{RED}" stroke-width="1.4"/>'
        f'<text class="type" font-size="7" font-weight="700" fill="{RED}" letter-spacing=".6">'
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
        text(W / 2, 84, "The Case of", "serif", 24, GOLD, font_style="italic", text_anchor="middle"),
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
        f'<g transform="translate(790 842) scale(.4)">{SMILEY.format(c=RED)}'
        + "".join(f'<circle cx="{a}" cy="{b}" r="{r}" fill="{RED}" opacity=".85"/>' for a, b, r in SPATTER)
        + '</g>',
    ]

    sheet = [paper("sheet", px, py, pw, ph)]
    sheet.append(f'<g filter="url(#rough)" fill="none" stroke="#7b5326">'
                 f'<circle cx="{px + pw - 120}" cy="{py + ph - 70}" r="47" stroke-width="3.5" opacity=".16"/>'
                 f'<circle cx="{px + pw - 116}" cy="{py + ph - 66}" r="44" stroke-width="1.2" opacity=".12"/></g>')
    sheet.append(f'<path d="M{px + 40} {py + 46}V{py - 14}a10 10 0 0 1 20 0V{py + 40}a6 6 0 0 1 -12 0V{py - 6}" '
                 f'fill="none" stroke="url(#steel)" stroke-width="2.6" stroke-linecap="round"/>')
    sheet.append(fingerprint(px + pw - 128, py + 158))
    tx = px + 52
    y = py + 60
    for label, value in FILE:
        dots = "." * (14 - len(label)) if len(label) < 12 else ".."
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
    note_x, note_y = px + pw - 372, py + ph - 24
    sheet.append(f'<g transform="rotate(-3 {note_x} {note_y})">'
                 + text(note_x, note_y, MARGIN_NOTE, "hand", 23, RED, opacity=".88")
                 + f'<path d="M{note_x + 352} {note_y - 18}c14 10 16 26 6 40m0 0l-2-10m2 10l9-5" fill="none" '
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
    W, H = 880, 660
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
        red_john(742, 34, .68),
        text(W / 2, 64, "EXHIBITS", "type", 12, GOLD, text_anchor="middle", letter_spacing="6"),
        text(W / 2, 92, "the memory palace: everything he carries into a case", "serif", 21, "#b9ae99", font_style="italic",
             text_anchor="middle"),
        f'<g fill="none" stroke="#000" stroke-opacity=".5" stroke-width="2.4" transform="translate(1.5 3)">{thread_paths}</g>',
        f'<g fill="none" stroke="{RED}" stroke-width="1.5">{thread_paths}</g>',
        "".join(cards),
        "".join(pin(x, y) for x, y in pins),
        teacup(92, 606),
        f'<g transform="rotate(-2 170 606)">'
        + text(170, 612, "tyger, tyger, burning bright…", "hand", 24, RED, opacity=".72") + "</g>",
        text(W - 46, H - 40, f"{sum(len(i) for _, i in STACK)} items logged", "type", 10.5, "#6f675b",
             text_anchor="end", letter_spacing="1.5"),
    ]
    defs = (GRAIN + ROUGH + PAPER + EDGE +
            '<radialGradient id="wall" cx=".5" cy=".42" r=".72">'
            '<stop offset="0" stop-color="#2d2620" stop-opacity=".95"/><stop offset="1" stop-color="#0b0a09" stop-opacity=".9"/>'
            '</radialGradient>'
            + TEA +
            '<radialGradient id="pinhead" cx=".38" cy=".35" r=".75"><stop offset="0" stop-color="#d4473a"/>'
            '<stop offset=".7" stop-color="#8d1d14"/><stop offset="1" stop-color="#5a0f0a"/></radialGradient>')
    label = "Evidence wall. " + " ".join(f"{c}: {', '.join(i)}." for c, i in STACK)
    return svg(W, H, label, "".join(body), defs)


TEA = ('<radialGradient id="tea" cx=".42" cy=".4" r=".7"><stop offset="0" stop-color="#9a6430"/>'
       '<stop offset=".75" stop-color="#5b3412"/><stop offset="1" stop-color="#3d220b"/></radialGradient>'
       '<radialGradient id="china" cx=".4" cy=".35" r=".8"><stop offset="0" stop-color="#fbfaf6"/>'
       '<stop offset="1" stop-color="#d9d4c8"/></radialGradient>')


def teacup(cx, cy):
    """Jane's cup and saucer, seen from above."""
    blue = "#4f74a3"
    return (
        f'<ellipse cx="{cx + 6}" cy="{cy + 10}" rx="48" ry="46" fill="#000" opacity=".5" filter="url(#lift)"/>'
        f'<circle cx="{cx}" cy="{cy}" r="46" fill="url(#china)" stroke="#bdb6a7"/>'
        f'<circle cx="{cx}" cy="{cy}" r="40" fill="none" stroke="{blue}" stroke-width="1.6" opacity=".8"/>'
        f'<circle cx="{cx}" cy="{cy}" r="31" fill="none" stroke="#000" stroke-opacity=".12" stroke-width="5"/>'
        f'<path d="M{cx + 24} {cy - 12}c16-6 26 2 24 12s-14 14-26 8" fill="none" stroke="url(#china)" stroke-width="6.5" stroke-linecap="round"/>'
        f'<path d="M{cx + 24} {cy - 12}c16-6 26 2 24 12s-14 14-26 8" fill="none" stroke="{blue}" stroke-width="1" opacity=".6"/>'
        f'<circle cx="{cx}" cy="{cy}" r="28" fill="url(#china)" stroke="{blue}" stroke-width="3"/>'
        f'<circle cx="{cx}" cy="{cy}" r="23" fill="url(#tea)"/>'
        f'<ellipse cx="{cx - 7}" cy="{cy - 8}" rx="8" ry="4" fill="#fff" opacity=".22" transform="rotate(-30 {cx - 7} {cy - 8})"/>'
    )


# ---------------------------------------------------------------- the clipping

def torn(x, y, w, h, seed):
    rng = random.Random(seed)
    pts = []
    for i in range(0, int(w) + 1, 6):
        pts.append((x + i, y + rng.uniform(-2.6, 2.6)))
    for i in range(0, int(h) + 1, 14):
        pts.append((x + w + rng.uniform(-.8, .8), y + i))
    for i in range(int(w), -1, -6):
        pts.append((x + i, y + h + rng.uniform(-2.6, 2.6)))
    for i in range(int(h), -1, -14):
        pts.append((x + rng.uniform(-.8, .8), y + i))
    return "M" + "L".join(f"{a:.1f},{b:.1f}" for a, b in pts) + "Z"


def clipping():
    W, H = 880, 560
    x, y, w, h = 130, 128, 620, 392
    cx = x + w / 2
    edge = torn(x, y, w, h, 8283)
    c = [
        f'<path d="{edge}" transform="translate(5 12)" fill="#000" opacity=".55" filter="url(#lift)"/>',
        f'<clipPath id="news"><path d="{edge}"/></clipPath>',
        f'<g clip-path="url(#news)"><rect x="{x - 5}" y="{y - 5}" width="{w + 10}" height="{h + 10}" fill="#e3dccb"/>'
        f'<rect x="{x - 5}" y="{y - 5}" width="{w + 10}" height="{h + 10}" filter="url(#mottle)" opacity=".55"/>'
        f'<rect x="{x - 5}" y="{y - 5}" width="{w + 10}" height="{h + 10}" filter="url(#fibre)"/>'
        f'<rect x="{x - 5}" y="{y - 5}" width="{w + 10}" height="{h + 10}" fill="url(#edge)"/></g>',
        text(cx, y + 48, "THE NIGHTLY BUILD", "serif", 30, INK, font_weight="600", text_anchor="middle", letter_spacing="7"),
        f'<path d="M{x + 30} {y + 62.5}h{w - 60}M{x + 30} {y + 66.5}h{w - 60}M{x + 30} {y + 86.5}h{w - 60}" stroke="{INK}" stroke-opacity=".7"/>',
        text(x + 32, y + 80, "NAMESPACE HACKATHON EDITION", "type", 9.5, FADED, letter_spacing="1.5"),
        text(x + w - 32, y + 80, "LATE FINAL", "type", 9.5, FADED, letter_spacing="1.5", text_anchor="end"),
        text(cx, y + 128, CLIPPING["headline"], "serif", 29, INK, font_weight="600", text_anchor="middle"),
    ]
    for i, line in enumerate(CLIPPING["deck"]):
        c.append(text(cx, y + 158 + i * 22, line, "serif", 17.5, "#4a4036", font_style="italic", text_anchor="middle"))
    c.append(f'<path d="M{x + 30} {y + 202.5}h{w - 60}" stroke="{INK}" stroke-opacity=".45"/>')
    c.append(f'<path d="M{cx + .5} {y + 216}v118" stroke="{INK}" stroke-opacity=".3"/>')
    for k, (head, body) in enumerate(CLIPPING["columns"]):
        colx = x + 34 + k * (w / 2 - 14)
        c.append(text(colx, y + 230, head, "type", 10, RED, font_weight="700", letter_spacing="1.2"))
        for j, line in enumerate(textwrap.wrap(body, 40)):
            c.append(text(colx, y + 256 + j * 21, line, "serif", 16.5, INK))
    sx, sy = x + w - 124, y + h - 40
    c.append(f'<g transform="rotate(-7 {sx} {sy})" opacity=".8" filter="url(#rough)">'
             f'<rect x="{sx - 82}" y="{sy - 21}" width="164" height="42" rx="3" fill="none" stroke="{RED}" stroke-width="2.6"/>'
             f'<rect x="{sx - 76}" y="{sy - 15}" width="152" height="30" rx="2" fill="none" stroke="{RED}" stroke-width="1.1"/>'
             + text(sx, sy + 6.5, "CASE CLOSED", "type", 17, RED, font_weight="700", text_anchor="middle", letter_spacing="2.5")
             + "</g>")
    c.append(f'<g transform="rotate(-4 {x + 40} {y + h - 26})">'
             + text(x + 40, y + h - 26, "called it.  — PJ", "hand", 24, RED, opacity=".85") + "</g>")

    body = [
        f'<rect width="{W}" height="{H}" rx="14" fill="{NIGHT}"/>',
        f'<rect width="{W}" height="{H}" rx="14" fill="url(#lamp)"/>',
        f'<rect width="{W}" height="{H}" rx="14" filter="url(#grain)"/>',
        f'<rect x="18.5" y="18.5" width="{W - 37}" height="{H - 37}" rx="6" fill="none" stroke="{GOLD}" stroke-opacity=".3"/>',
        text(W / 2, 64, "CASE CLOSED", "type", 12, GOLD, text_anchor="middle", letter_spacing="6"),
        text(W / 2, 92, "the one that made the papers", "serif", 21, "#b9ae99", font_style="italic", text_anchor="middle"),
        f'<g transform="rotate(1.1 {cx} {y + h / 2})">{"".join(c)}</g>',
    ]
    defs = (GRAIN + ROUGH + PAPER + EDGE +
            '<radialGradient id="lamp" cx=".5" cy=".4" r=".7">'
            '<stop offset="0" stop-color="#2b2520" stop-opacity=".9"/><stop offset="1" stop-color="#2b2520" stop-opacity="0"/>'
            '</radialGradient>')
    label = ("Case closed. Sambhaash AI at the Namespace Hackathon: " +
             " ".join(f"{hd.replace('  ·  ', ', ').title()}: {b}" for hd, b in CLIPPING["columns"]))
    return svg(W, H, label, "".join(body), defs)


# ---------------------------------------------------------------- the couch

def chesterfield():
    leather, roll = "url(#leather)", "url(#roll)"
    rows = [168, 192, 214]
    buttons = [(x, y) for r, y in enumerate(rows) for x in range(262 + (r % 2) * 22, 628, 44)]
    creases = []
    for (ax, ay) in buttons:
        for (bx, by) in buttons:
            if 0 < by - ay < 30 and abs(bx - ax) == 22:
                creases.append(f"M{ax} {ay}L{bx} {by}")
    tufting = (f'<path d="{"".join(creases)}" stroke="#1f1108" stroke-opacity=".45" stroke-width="1.3"/>'
               f'<path d="{"".join(creases)}" stroke="#b07a48" stroke-opacity=".22" transform="translate(0 1.4)"/>'
               + "".join(f'<circle cx="{x}" cy="{y}" r="2.3" fill="#24130a"/><circle cx="{x - .6}" cy="{y - .7}" r=".8" fill="#c08850" opacity=".6"/>'
                         for x, y in buttons))

    def arm(cx):
        fan = "".join(f'M{cx} 186L{cx + 34 * math.cos(a):.1f} {186 - 34 * math.sin(a):.1f}'
                      for a in [i * 3.14159 / 10 for i in range(1, 10)])
        nails = "".join(f'<circle cx="{cx + 37 * math.cos(a):.1f}" cy="{188 - 37 * math.sin(a):.1f}" r="1.3" fill="#d4ae6e" opacity=".75"/>'
                        for a in [i * 3.14159 / 16 for i in range(0, 17)])
        nails += "".join(f'<circle cx="{cx + dx}" cy="{y}" r="1.3" fill="#d4ae6e" opacity=".75"/>'
                         for dx in (-37, 37) for y in range(196, 286, 9))
        return (f'<path d="M{cx - 40} 290V188C{cx - 40} 162 {cx - 22} 146 {cx} 146S{cx + 40} 162 {cx + 40} 188V290z" fill="{leather}"/>'
                f'<path d="M{cx - 40} 188C{cx - 40} 162 {cx - 22} 146 {cx} 146S{cx + 40} 162 {cx + 40} 188" fill="none" stroke="#b9824e" stroke-opacity=".5" stroke-width="2"/>'
                f'<path d="{fan}" stroke="#1f1108" stroke-opacity=".5" stroke-width="1.2"/>'
                f'<circle cx="{cx}" cy="186" r="4" fill="{roll}"/><circle cx="{cx}" cy="186" r="4" fill="none" stroke="#24130a"/>'
                + nails)

    return (
        '<ellipse cx="440" cy="304" rx="300" ry="10" fill="#000" opacity=".6" filter="url(#lift)"/>'
        + "".join(f'<path d="M{x} 288h18v8c0 6-4 9-9 9s-9-3-9-9z" fill="url(#wood)"/>' for x in (222, 300, 562, 640))
        + f'<rect x="246" y="146" width="388" height="90" rx="20" fill="{leather}"/>'
        f'<path d="M262 149.5H618" stroke="#c48f58" stroke-opacity=".45" stroke-width="2.5" stroke-linecap="round"/>'
        + tufting
        + f'<path d="M244 222h392q8 0 8 8v24q0 8-8 8H244q-8 0-8-8v-24q0-8 8-8z" fill="url(#seat)"/>'
        f'<path d="M248 223.5h384" stroke="#d29a62" stroke-opacity=".5" stroke-width="2" stroke-linecap="round"/>'
        f'<path d="M440 224v36" stroke="#1f1108" stroke-opacity=".55" stroke-width="1.4"/>'
        f'<rect x="238" y="260" width="404" height="30" rx="4" fill="#3a2112"/>'
        + "".join(f'<circle cx="{x}" cy="267" r="1.3" fill="#d4ae6e" opacity=".7"/>' for x in range(246, 636, 9))
        + arm(240) + arm(640)
    )


def jane():
    """Patrick Jane asleep flat on his back on the seat, ankles crossed on the right arm."""
    skin_dk, hair_dk, hair_hi = "#b98463", "#8a6430", "#ecd08f"
    suit, waistcoat = "url(#suit)", "#3e3933"

    # head drawn upright in profile (facing +x), then laid down face-up with rotate(-84)
    curls = [(12, -21, 4.8), (5, -28.5, 5.6), (-4, -32, 5.8), (-13.5, -30, 5.8), (-21.5, -24.5, 5.8),
             (-27, -15.5, 5.6), (-29, -5.5, 5.4), (-28, 4.5, 5.2), (-25, 13, 5), (-19.5, 19, 4.6), (-13, 21.5, 4.2)]
    waves = [(6, -27, 14), (-3, -30, 18), (-14, -27, 25), (-22, -20, 40), (-26, -10, 60), (-26, 1, 80),
             (-23, 11, 95), (-6, -23, 20), (-15, -17, 40), (-20, -6, 70), (2, -19, 15), (-12, -8, 55), (-17, 6, 85)]
    hair = (
        '<path d="M14 -17C13 -29 2 -34 -9 -33C-21 -32 -29 -23 -30 -10C-31 2 -28 12 -23 18C-19 22 -14 24 -10 22'
        'C-11 15 -10 9 -7 4C-4 -3 1 -9 7 -12C10 -14 12 -15 14 -17Z" fill="url(#hairF)"/>'
        + "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="url(#hairF)"/>' for x, y, r in curls)
        + "".join(f'<path transform="rotate({a} {x} {y})" d="M{x - 6} {y}q3-3.4 6 0t6 0" fill="none" stroke="{hair_dk}" '
                  f'stroke-width="1.1" stroke-linecap="round" opacity=".55"/>' for x, y, a in waves)
        + "".join(f'<path transform="rotate({a} {x} {y - 2})" d="M{x - 4} {y - 2}q2-2.4 4 0" fill="none" stroke="{hair_hi}" '
                  f'stroke-width="1.2" stroke-linecap="round" opacity=".7"/>' for x, y, a in waves[::2])
    )
    head = (
        '<path d="M8 28L9 44L-11 44L-12 22z" fill="#cf9b77"/>'
        f'<path d="M2 30C4 36 5 40 5 44" fill="none" stroke="{skin_dk}" stroke-width="1.6" opacity=".5"/>'
        '<path d="M-2 -27C8 -28 16 -22 18 -12C19 -8 19 -6 18 -4C19 -1 21 2 24 8C22 10 20 10 19 10.5'
        'C20 12 20 13 19.5 14L18 15C19.5 16 19.5 17.5 18.5 18.5C17 19.5 16.5 20 17 22C17.5 25 15 27 11 27.5'
        'C9 28 8 29 8 31L-12 31L-12 24C-18 18 -21 8 -21 -2C-21 -18 -12 -27 -2 -27Z" fill="url(#skinF)"/>'
        f'<path d="M-4 15C1 21 6 24 12 26" fill="none" stroke="{skin_dk}" stroke-width="2" stroke-linecap="round" opacity=".3"/>'
        f'<path d="M15 2C17 6 19 8 21.5 8.5" fill="none" stroke="{skin_dk}" stroke-width="1.6" stroke-linecap="round" opacity=".6"/>'
        '<path d="M8 -3.2Q12 -.4 16.2 -2.8" fill="none" stroke="#4e2f1f" stroke-width="1.2" stroke-linecap="round"/>'
        '<path d="M10.6 -1.7l-.2 1.2M13.4 -1.7l.2 1.2" stroke="#4e2f1f" stroke-width=".6" stroke-linecap="round" opacity=".8"/>'
        '<path d="M8 -7.6Q12.5 -9.8 17.2 -7.4" fill="none" stroke="#a57a42" stroke-width="1.5" stroke-linecap="round" opacity=".9"/>'
        '<path d="M19.4 9.2q1.4-1.1 2.6-.1" fill="none" stroke="#8f5a40" stroke-width="1" stroke-linecap="round"/>'
        '<path d="M15.4 14.9q1.8 1.3 3.8.4" fill="none" stroke="#8f5a40" stroke-width="1.1" stroke-linecap="round"/>'
        + hair
        + '<ellipse cx="-6.5" cy="2.5" rx="4.4" ry="6.6" fill="#cf9b77"/>'
        '<path d="M-5 -1.5c2.4 1 2.6 5.5.4 7.6" fill="none" stroke="#8f5a40" stroke-width="1" stroke-linecap="round"/>'
        + "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="url(#hairF)"/>' for x, y, r in [(-9, -5, 4.6), (-3.5, -8, 4)])
    )

    torso = (
        f'<path d="M338 194C352 184 366 180 384 178C410 176 432 180 452 186C464 190 474 192 486 194L490 222L344 222'
        f'C339 214 337 204 338 194Z" fill="{suit}"/>'
        f'<path d="M342 192C356 184 368 182 384 180C410 178 432 182 452 188C464 192 474 194 486 196L486 204'
        f'C474 202 464 200 452 196C432 190 410 186 384 188C368 190 356 192 344 199Z" fill="{waistcoat}"/>'
        + "".join(f'<circle cx="{x}" cy="{y}" r="1.5" fill="#191613"/><circle cx="{x - .4}" cy="{y - .5}" r=".5" fill="#a39a8c"/>'
                  for x, y in [(394, 182.6), (414, 182.4), (434, 185), (454, 190.6)])
        + f'<path d="M352 196C376 194 406 194 432 198C452 201 470 206 488 212" fill="none" stroke="#17140f" stroke-width="1.4" opacity=".7"/>'
        f'<path d="M352 198.4C376 196.4 406 196.4 432 200.4" fill="none" stroke="#7c7266" stroke-width=".9" opacity=".45"/>'
        f'<path d="M334 188C340 183 350 182 358 186L355 198C349 195 342 196 336 200Z" fill="#ece8de"/>'
        f'<path d="M337 186C341 181 346 180 351 181L351 188C346 187 341 188 337 191z" fill="#f6f3ec"/>'
        f'<path d="M350 182C355 181 359 183 361 186L356 192C355 189 353 188 350 188z" fill="#ddd8cc"/>'
    )
    arm = (
        f'<path d="M346 194C366 197 390 204 412 210C421 212 423 220 414 222C390 220 364 214 344 208Z" fill="{suit}"/>'
        f'<path d="M354 200C374 204 394 210 410 214" fill="none" stroke="#17140f" stroke-width="1" opacity=".4"/>'
        f'<path d="M405 207C417 200 427 194 435 188L446 198C436 206 426 214 416 221Z" fill="{suit}"/>'
        f'<path d="M433 186l7-4 9 12-6 5z" fill="#ece8de"/>'
        f'<ellipse cx="455" cy="188" rx="11" ry="7" transform="rotate(-14 455 188)" fill="{skin_dk}"/>'
        f'<ellipse cx="454" cy="185.5" rx="10" ry="6.4" transform="rotate(-14 454 185.5)" fill="url(#skinF)"/>'
        f'<path d="M448 183l8 2.6M449 180.4l8 2.8M452 178.8l6 2" stroke="{skin_dk}" stroke-width=".9" stroke-linecap="round"/>'
    )
    legs = (
        f'<path d="M476 190C498 186 526 180 554 177C578 174 600 162 618 149L624 164C606 174 588 186 568 198'
        f'C548 208 518 216 486 218Z" fill="#26231f"/>'
        f'<path d="M616 146C620 138 626 130 632 123C636 117 644 116 647 121C650 128 642 142 634 156C630 161 624 163 619 161Z" fill="#2a1a0e"/>'
        f'<path d="M478 194C500 190 528 184 556 182C580 178 604 166 624 154L632 170C612 178 592 192 572 204'
        f'C552 214 520 222 488 223Z" fill="{suit}"/>'
        f'<path d="M486 197C508 193 532 188 556 185.5C578 182 600 172 620 159" fill="none" stroke="#8a8073" stroke-width=".9" opacity=".5"/>'
        f'<path d="M552 186c4 3 9 4 14 3M560 196c3 2 7 3 10 2" fill="none" stroke="#17140f" stroke-width="1" opacity=".45"/>'
        f'<path d="M621 154l6-2.4 7 16.6-5 2.4z" fill="#1d1916"/>'
        f'<path d="M626 153C630 145 636 137 642 129C646 123 654 122 657 127C660 134 652 149 644 163C640 168 634 171 628 169Z" fill="url(#shoe)"/>'
        f'<path d="M657 127C660 134 652 149 644 163C640 168 634 171 628 169" fill="none" stroke="#120a05" stroke-width="2.2" stroke-linecap="round"/>'
        f'<path d="M635 142c4-5 8-10 13-13" fill="none" stroke="#c7925e" stroke-width="1.1" stroke-linecap="round" opacity=".55"/>'
    )
    return (torso + legs + arm
            + f'<g transform="translate(306 196) rotate(-84) scale(.78)">{head}</g>')


def teacup_side(cx, floor):
    return (
        f'<ellipse cx="{cx}" cy="{floor - 1}" rx="27" ry="5.5" fill="#000" opacity=".5" filter="url(#lift)"/>'
        f'<ellipse cx="{cx}" cy="{floor - 4}" rx="26" ry="5" fill="url(#chinaSide)"/>'
        f'<ellipse cx="{cx}" cy="{floor - 5}" rx="17" ry="2.6" fill="#cfc8b8"/>'
        f'<path d="M{cx + 15} {floor - 21}c10-3 11 10 1 11" fill="none" stroke="url(#chinaSide)" stroke-width="3.4"/>'
        f'<path d="M{cx - 16} {floor - 26}C{cx - 16} {floor - 12} {cx - 9} {floor - 6} {cx} {floor - 6}S{cx + 16} {floor - 12} {cx + 16} {floor - 26}z" fill="url(#chinaSide)"/>'
        f'<path d="M{cx - 15.6} {floor - 21.5}h31.2" stroke="#4f74a3" stroke-width="2"/>'
        f'<ellipse cx="{cx}" cy="{floor - 26}" rx="16" ry="3.6" fill="#f6f3ec" stroke="#c8c0b0" stroke-width=".8"/>'
        f'<ellipse cx="{cx}" cy="{floor - 25.6}" rx="13.4" ry="2.5" fill="#6b3e18"/>'
        f'<g class="steam" fill="none" stroke="#e9dcc4" stroke-width="1.6" stroke-linecap="round">'
        f'<path d="M{cx - 4} {floor - 32}c-5-6 4-10 0-16s3-9 1-13"/>'
        f'<path d="M{cx + 5} {floor - 34}c-4-5 4-8 0-13s3-7 1-10" style="animation-delay:1.6s"/></g>'
    )


def floor_lamp(x, floor):
    return (
        f'<path d="M{x - 30} 158L{x + 30} 158L{x + 120} {floor}L{x - 260} {floor}Z" fill="url(#cone)"/>'
        f'<ellipse cx="{x}" cy="{floor - 1}" rx="18" ry="4" fill="#1a1510"/>'
        f'<rect x="{x - 1.6}" y="150" width="3.2" height="{floor - 151}" fill="url(#brass)"/>'
        f'<path d="M{x - 18} 118h36l11 40h-58z" fill="url(#shade)"/>'
        f'<ellipse cx="{x}" cy="158" rx="29" ry="4" fill="#fff1c9" opacity=".75"/>'
    )


def couch():
    W, H = 880, 380
    floor = 304
    zs = "".join(
        f'<g class="z" style="animation-delay:{i * 1.3}s">'
        + text(300 - i * 10, 160 - i * 15, "z", "serif", 13 + i * 4, GOLD, font_style="italic", opacity=f"{.9 - i * .2}")
        + "</g>" for i in range(3))
    scene = chesterfield() + jane() + zs + teacup_side(166, floor) + floor_lamp(776, floor)
    body = [
        f'<rect width="{W}" height="{H}" rx="14" fill="{NIGHT}"/>',
        f'<rect width="{W}" height="{H}" rx="14" fill="url(#pool)"/>',
        f'<rect width="{W}" height="{H}" rx="14" fill="url(#lampglow)"/>',
        f'<path d="M30 {floor + 20 + 4}H{W - 30}" stroke="#000" stroke-opacity=".0"/>',
        f'<rect width="{W}" height="{H}" rx="14" filter="url(#grain)"/>',
        f'<rect x="18.5" y="18.5" width="{W - 37}" height="{H - 37}" rx="6" fill="none" stroke="{GOLD}" stroke-opacity=".3"/>',
        text(W / 2, 56, "THE CONSULTANT IS RESTING HIS EYES", "type", 12, GOLD, text_anchor="middle", letter_spacing="5"),
        text(W / 2, 84, "leave a lead. he’ll have read it before he wakes.", "serif", 21, "#b9ae99",
             font_style="italic", text_anchor="middle"),
        f'<g transform="translate(0 22)">{scene}</g>',
    ]
    defs = (GRAIN + PAPER +
            '<radialGradient id="pool" cx=".5" cy=".7" r=".55"><stop offset="0" stop-color="#3a2f24" stop-opacity=".85"/>'
            '<stop offset="1" stop-color="#3a2f24" stop-opacity="0"/></radialGradient>'
            '<radialGradient id="lampglow" cx=".88" cy=".42" r=".42"><stop offset="0" stop-color="#e8b86a" stop-opacity=".22"/>'
            '<stop offset="1" stop-color="#e8b86a" stop-opacity="0"/></radialGradient>'
            '<linearGradient id="cone" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffd995" stop-opacity=".12"/>'
            '<stop offset="1" stop-color="#ffd995" stop-opacity="0"/></linearGradient>'
            '<linearGradient id="shade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#d9b06a"/>'
            '<stop offset="1" stop-color="#f6dca2"/></linearGradient>'
            '<linearGradient id="brass" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#6b5530"/>'
            '<stop offset=".5" stop-color="#c9a65e"/><stop offset="1" stop-color="#5a4626"/></linearGradient>'
            '<linearGradient id="leather" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#80502b"/>'
            '<stop offset="1" stop-color="#43250f"/></linearGradient>'
            '<linearGradient id="seat" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8f5a32"/>'
            '<stop offset="1" stop-color="#4f2c15"/></linearGradient>'
            '<radialGradient id="roll" cx=".4" cy=".35" r=".7"><stop offset="0" stop-color="#a06a3c"/>'
            '<stop offset="1" stop-color="#5a3319"/></radialGradient>'
            '<linearGradient id="wood" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#1c0f07"/>'
            '<stop offset=".45" stop-color="#5a3519"/><stop offset="1" stop-color="#1c0f07"/></linearGradient>'
            '<linearGradient id="suit" gradientUnits="userSpaceOnUse" x1="0" y1="110" x2="0" y2="225">'
            '<stop offset="0" stop-color="#6a6158"/><stop offset=".35" stop-color="#4a443d"/><stop offset="1" stop-color="#25221e"/></linearGradient>'
            '<linearGradient id="shoe" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#8a5a32"/>'
            '<stop offset="1" stop-color="#3a2212"/></linearGradient>'
            '<linearGradient id="skinF" x1="1" y1="0" x2="0" y2="0"><stop offset="0" stop-color="#f0c7a2"/>'
            '<stop offset=".6" stop-color="#dcab84"/><stop offset="1" stop-color="#c08a66"/></linearGradient>'
            '<linearGradient id="hairF" gradientUnits="userSpaceOnUse" x1="18" y1="0" x2="-20" y2="0">'
            '<stop offset="0" stop-color="#e2bd72"/><stop offset=".5" stop-color="#c79a4e"/><stop offset="1" stop-color="#9a7136"/></linearGradient>'
            '<linearGradient id="chinaSide" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#d7d1c4"/>'
            '<stop offset=".35" stop-color="#fbfaf6"/><stop offset="1" stop-color="#bdb6a7"/></linearGradient>')
    css = ("@keyframes drift{0%,100%{transform:translate(0,0)}50%{transform:translate(-4px,-5px)}}"
           ".z{animation:drift 3.9s ease-in-out infinite}"
           "@keyframes rise{0%{opacity:0;transform:translateY(6px)}40%{opacity:.4}100%{opacity:0;transform:translateY(-10px)}}"
           ".steam path{opacity:.3;animation:rise 3.2s ease-in-out infinite}"
           "@media (prefers-reduced-motion:reduce){.z,.steam path{animation:none}}")
    return svg(W, H, "Patrick Jane asleep on his brown leather couch, teacup on the floor. The consultant is resting his eyes.",
               "".join(body), defs, css)


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
    files = {"dossier.svg": dossier(), "closed.svg": clipping(), "evidence.svg": evidence(), "couch.svg": couch()}
    for n, (slug, label, _) in enumerate(LEADS, 1):
        files[f"lead-{slug}.svg"] = lead(n, label)
    for name, content in files.items():
        (ASSETS / name).write_text(content)
        print(f"{name:22} {len(content) / 1024:6.1f} KB")


if __name__ == "__main__":
    main()
