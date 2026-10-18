#!/usr/bin/env python3
"""Regenerates assets/*.svg for the profile README.

Edit STACK (or the text constants) below, then run:  python3 scripts/build.py
"""
import html
import math
import random
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
CACHE = Path(__file__).resolve().parent / ".cache"

NAME = "Rahul L S"
HANDLE = "Rahul-8283"
ROLES = [
    ("Web", "Full-stack developer"),
    ("Apps", "Cross-platform developer"),
    ("AI", "AI systems builder"),
]
MOTTO = "building, breaking, becoming…"
PLAN = [
    "full-stack developer, gone deep on agentic AI.",
    "i build products where the model is one moving part of a real system:",
    "agents that hold a phone call, retrieval that walks a knowledge graph,",
    "and routers that pick the smallest model that can do the job.",
    "web, mobile or desktop: whatever screen it has to reach.",
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

SANS = "-apple-system,BlinkMacSystemFont,'SF Pro Text','Helvetica Neue','Segoe UI',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,'SF Mono',SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
LIGHTS = (("#ff5f57", 0), ("#febc2e", 20), ("#28c840", 40))


def esc(s):
    return html.escape(s, quote=False)


def lights(x, y):
    return "".join(f'<circle cx="{x + dx}" cy="{y}" r="6" fill="{c}"/>' for c, dx in LIGHTS)


# ---------------------------------------------------------------- icons

def fetch(url, path):
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["curl", "-fsSL", url, "-o", str(path)], check=True)
    return path.read_text()


def scope(svg, prefix):
    for i in set(re.findall(r'\bid="([^"]+)"', svg)):
        svg = (svg.replace(f'id="{i}"', f'id="{prefix}-{i}"')
                  .replace(f"url(#{i})", f"url(#{prefix}-{i})")
                  .replace(f'href="#{i}"', f'href="#{prefix}-{i}"'))
    return svg


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


# ---------------------------------------------------------------- wallpaper

W, H = 880, 560


def ridge(rng, base, amp, peaks=()):
    ph = [rng.uniform(0, math.tau) for _ in range(4)]
    pts = []
    for x in range(-12, W + 13, 6):
        y = base - amp * (0.55 * math.sin(x / 170 + ph[0]) + 0.28 * math.sin(x / 71 + ph[1])
                          + 0.12 * math.sin(x / 29 + ph[2]) + 0.05 * math.sin(x / 11 + ph[3]))
        for px, height, width in peaks:
            y -= height * math.exp(-(((x - px) / width) ** 2))
        pts.append(f"L{x},{y:.1f}")
    return f"M-12,{H + 12} {' '.join(pts)} L{W + 12},{H + 12}Z"


def conifer(rng, x, base, h):
    tiers = max(5, int(h / 8))
    left, right = [], []
    for i in range(1, tiers + 1):
        t = i / tiers
        y = base - h + h * 0.94 * t
        half = h * 0.2 * t * rng.uniform(0.8, 1.15)
        lift = h / tiers * 0.3
        left += [(x - half, y), (x - half * 0.42, y - lift)]
        right += [(x + half, y), (x + half * 0.42, y - lift)]
    pts = [(x, base - h)] + left[:-1] + [(x - 1.5, base), (x + 1.5, base)] + right[:-1][::-1]
    return "M" + " L".join(f"{px:.1f},{py:.1f}" for px, py in pts) + "Z"


def wallpaper():
    rng = random.Random(8283)
    layers = [
        ("r1", 338, 24, [(236, 52, 58), (300, 20, 30), (640, 30, 110)], "#a3b2bf", "#cfd6da"),
        ("r2", 380, 30, [(520, 26, 90)], "#8195a5", "#bcc7ce"),
        ("r3", 424, 32, [(120, 22, 80)], "#5b6f7f", "#9aa9b3"),
        ("r4", 474, 24, [(760, 30, 120)], "#34444d", "#5e6f77"),
    ]
    defs = [
        '<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#b4c0c9"/><stop offset=".55" stop-color="#d6dbdc"/>'
        '<stop offset="1" stop-color="#ebe6db"/></linearGradient>',
        '<radialGradient id="glow" cx=".3" cy=".34" r=".55">'
        '<stop offset="0" stop-color="#fff" stop-opacity=".55"/>'
        '<stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>',
    ]
    body = [f'<rect width="{W}" height="{H}" fill="url(#sky)"/>',
            f'<rect width="{W}" height="{H}" fill="url(#glow)"/>']
    for gid, base, amp, peaks, top, bottom in layers:
        defs.append(f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="0" y1="{base - 60}" '
                    f'x2="0" y2="{base + 70}"><stop offset="0" stop-color="{top}"/>'
                    f'<stop offset="1" stop-color="{bottom}"/></linearGradient>')
        body.append(f'<path d="{ridge(rng, base, amp, peaks)}" fill="url(#{gid})"/>')

    # Tree line: sparse on the left, tall and dense on the right, as in the photo.
    back, front = [], []
    x = -10
    while x < W + 10:
        back.append(conifer(rng, x, 520 + rng.uniform(-6, 6), rng.uniform(34, 62)))
        x += rng.uniform(9, 20)
    x = -6
    while x < W + 10:
        t = x / W
        tall = 40 + 26 * max(0, 1 - t * 4) + 120 * max(0, (t - 0.55) / 0.45) ** 1.4
        front.append(conifer(rng, x, 548 + rng.uniform(-4, 6), tall * rng.uniform(0.7, 1.15)))
        x += rng.uniform(13, 30)
    body.append(f'<path d="{" ".join(back)}" fill="#2a3a3c"/>')
    body.append(f'<path d="{ridge(rng, 532, 8)}" fill="#172120"/>')
    body.append(f'<g id="front"><path d="{" ".join(front)}" fill="#0f1716"/>'
                f'<rect y="{H - 10}" width="{W}" height="10" fill="#0f1716"/></g>')

    mist = "".join(
        f'<ellipse class="mist m{i}" cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#fff" '
        f'opacity="{op}" filter="url(#soft)"/>'
        for i, (cx, cy, rx, ry, op) in enumerate(
            [(210, 398, 250, 16, .5), (640, 440, 300, 18, .42), (380, 492, 340, 14, .3)])
    )
    return defs, "".join(body), mist


# ---------------------------------------------------------------- desktop

def glass(wid, x, y, w, h, tint):
    """Dark vibrancy panel: blurred wallpaper, tint, hairline borders."""
    return (
        f'<clipPath id="{wid}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="11"/></clipPath>'
        f'<rect x="{x}" y="{y + 10}" width="{w}" height="{h}" rx="11" fill="#0b1116" opacity=".55" '
        f'filter="url(#shadow)"/>'
        f'<g clip-path="url(#{wid})"><use href="#wp" filter="url(#vibrancy)"/>'
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{tint}"/></g>'
        f'<rect x="{x - .5}" y="{y - .5}" width="{w + 1}" height="{h + 1}" rx="11.5" fill="none" '
        f'stroke="#000" stroke-opacity=".45"/>'
        f'<rect x="{x + .5}" y="{y + .5}" width="{w - 1}" height="{h - 1}" rx="10.5" fill="none" '
        f'stroke="#fff" stroke-opacity=".16"/>'
    )


def menubar():
    items = "".join(f'<tspan dx="17">{m}</tspan>' for m in ["File", "Edit", "View", "Go", "Window", "Help"])
    return (
        f'<rect width="{W}" height="26" fill="#fff" opacity=".3"/>'
        '<path d="M16 18.5l5.2-9 2.9 4.6 1.7-2.4 4.2 6.8z" fill="#1c1f23"/>'
        f'<text x="40" y="17.5" class="ui" font-size="13" fill="#1c1f23">'
        f'<tspan font-weight="700">{esc(NAME)}</tspan>{items}</text>'
        # battery, wi-fi, control centre, clock
        '<g fill="none" stroke="#1c1f23" stroke-width="1.1">'
        '<rect x="733.5" y="7.5" width="22" height="11" rx="3" opacity=".5"/>'
        '<path d="M770.5 12.6a8.6 8.6 0 0111 0M772.7 15a5.2 5.2 0 016.6 0" stroke-linecap="round" stroke-width="1.5"/>'
        '<rect x="796.5" y="7.5" width="12" height="4.6" rx="2.3"/>'
        '<rect x="796.5" y="14" width="12" height="4.6" rx="2.3"/></g>'
        '<g fill="#1c1f23"><rect x="735" y="9" width="15" height="8" rx="1.7"/>'
        '<path d="M757 11.2c.9.2 1.4.9 1.4 1.8s-.5 1.6-1.4 1.8z" opacity=".5"/>'
        '<circle cx="776" cy="17.2" r="1.3"/>'
        '<circle cx="806.2" cy="9.8" r="1.5"/><circle cx="798.8" cy="16.3" r="1.5"/></g>'
        '<text x="864" y="17.5" class="ui" font-size="13" fill="#1c1f23" text-anchor="end">9:41 AM</text>'
    )


def about(x, y, w, h):
    cx = x + w / 2
    my = y + 72
    scale = 0.36
    out = [
        glass("aboutClip", x, y, w, h, "rgba(27,31,36,.72)"),
        lights(x + 18, y + 18),
        f'<clipPath id="medal"><circle cx="{cx}" cy="{my}" r="38"/></clipPath>',
        f'<g clip-path="url(#medal)"><use href="#wp" transform="translate({cx - 236 * scale:.1f} '
        f'{my - 330 * scale:.1f}) scale({scale})"/></g>',
        f'<circle cx="{cx}" cy="{my}" r="38" fill="none" stroke="#fff" stroke-opacity=".3" stroke-width="1.5"/>',
        f'<text x="{cx}" y="{y + 144}" class="ui" font-size="22" font-weight="700" fill="#f4f6f7" '
        f'text-anchor="middle">{esc(NAME)}</text>',
        f'<text x="{cx}" y="{y + 163}" class="ui" font-size="12" fill="#9da7b0" '
        f'text-anchor="middle">{esc(HANDLE)}</text>',
    ]
    for i, (label, value) in enumerate(ROLES):
        ry = y + 198 + i * 22
        out.append(f'<text x="{x + 92}" y="{ry}" class="ui" font-size="12.5" fill="#9da7b0" '
                   f'text-anchor="end">{esc(label)}</text>')
        out.append(f'<text x="{x + 102}" y="{ry}" class="ui" font-size="12.5" fill="#eef1f3">{esc(value)}</text>')
    return "".join(out)


CW, LH, DUR = 7.5, 19, 6.0
PROMPT = "rahul@github ~ %"


def mono(x, y, s, fill, extra=""):
    return (f'<text x="{x}" y="{y}" class="mono" font-size="12.5" fill="{fill}" '
            f'textLength="{len(s) * CW}" lengthAdjust="spacing"{extra}>{esc(s)}</text>')


def appear(t):
    return (f'<animate attributeName="opacity" dur="{DUR}s" fill="freeze" calcMode="discrete" '
            f'values="0;1" keyTimes="0;{t / DUR:.4f}"/>')


def terminal(x, y, w, h):
    session = [
        ("whoami", [[("rahul-ls", "#d9dee2", 0)]]),
        ("ls work/", [[(d, "#a3c2dc", i * 11) for i, d in enumerate(["web/", "mobile/", "desktop/", "ai/"])]]),
        ("cat .motto", [[(MOTTO, "#d9dee2", 0)]]),
    ]
    out = [
        glass("termClip", x, y, w, h, "rgba(18,21,25,.82)"),
        f'<g clip-path="url(#termClip)"><rect x="{x}" y="{y}" width="{w}" height="28" fill="#fff" opacity=".07"/></g>',
        f'<path d="M{x} {y + 28.5}h{w}" stroke="#000" stroke-opacity=".5"/>',
        lights(x + 18, y + 14),
        f'<text x="{x + w / 2}" y="{y + 18.5}" class="ui" font-size="12" font-weight="600" fill="#aab2ba" '
        f'text-anchor="middle">rahul — -zsh — 58×9</text>',
    ]
    return "".join(out) + typed(x + 16, y + 53, session)


def typed(tx, ty, session):
    """Prompt/command/output lines; commands type themselves once, then the cursor blinks."""
    cmd_x = tx + (len(PROMPT) + 1) * CW
    out = []
    cursor = [(0.0, cmd_x, ty)]
    t, line = 0.9, 0
    for n, (cmd, outputs) in enumerate(session):
        ly = ty + line * LH
        shown = "" if n == 0 else appear(prompt_at)
        out.append(f'<g>{shown}{mono(tx, ly, PROMPT, "#8d97a1")}</g>')
        if n:
            cursor.append((prompt_at, cmd_x, ly))
        widths, times = ["0"], ["0"]
        for k in range(1, len(cmd) + 1):
            widths.append(f"{k * CW}")
            times.append(f"{(t + (k - 1) * 0.075) / DUR:.4f}")
            cursor.append((t + (k - 1) * 0.075, cmd_x + k * CW, ly))
        t_end = t + len(cmd) * 0.075
        out.append(
            f'<clipPath id="type{n}"><rect x="{cmd_x}" y="{ly - 14}" width="{len(cmd) * CW}" height="20">'
            f'<animate attributeName="width" dur="{DUR}s" fill="freeze" calcMode="discrete" '
            f'values="{";".join(widths)}" keyTimes="{";".join(times)}"/></rect></clipPath>'
            f'<g clip-path="url(#type{n})">{mono(cmd_x, ly, cmd, "#f2f4f5")}</g>'
        )
        line += 1
        for row in outputs:
            cells = "".join(mono(tx + col * CW, ty + line * LH, s, fill) for s, fill, col in row)
            out.append(f"<g>{appear(t_end + 0.3)}{cells}</g>")
            line += 1
        prompt_at = t_end + 0.5
        t = t_end + 1.1
    ly = ty + line * LH
    out.append(f'<g>{appear(prompt_at)}{mono(tx, ly, PROMPT, "#8d97a1")}</g>')
    cursor.append((prompt_at, cmd_x, ly))
    times = ";".join(f"{c[0] / DUR:.4f}" for c in cursor)
    out.append(
        f'<rect x="{cmd_x}" y="{ly - 12}" width="{CW}" height="15" fill="#d9dee2">'
        f'<animate attributeName="x" dur="{DUR}s" fill="freeze" calcMode="discrete" '
        f'values="{";".join(f"{c[1]}" for c in cursor)}" keyTimes="{times}"/>'
        f'<animate attributeName="y" dur="{DUR}s" fill="freeze" calcMode="discrete" '
        f'values="{";".join(f"{c[2] - 12}" for c in cursor)}" keyTimes="{times}"/>'
        f'<animate attributeName="opacity" begin="{prompt_at}s" dur="1.1s" calcMode="discrete" '
        f'values="1;0" keyTimes="0;0.5" repeatCount="indefinite"/></rect>'
    )
    return "".join(out)


def desktop():
    defs, scene, mist = wallpaper()
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{esc(NAME)} — macOS desktop">
<style>
.ui{{font-family:{SANS}}}.mono{{font-family:{MONO}}}
.mist{{animation:drift 46s ease-in-out infinite alternate}}
.m1{{animation-duration:62s;animation-direction:alternate-reverse}}.m2{{animation-duration:54s}}
@keyframes drift{{from{{transform:translateX(-46px)}}to{{transform:translateX(46px)}}}}
@media (prefers-reduced-motion:reduce){{.mist{{animation:none}}}}
</style>
<defs>
{"".join(defs)}
<filter id="soft" x="-20%" y="-200%" width="140%" height="500%"><feGaussianBlur stdDeviation="16"/></filter>
<filter id="vibrancy" x="0" y="0" width="100%" height="100%"><feGaussianBlur stdDeviation="20"/><feColorMatrix type="saturate" values="1.4"/></filter>
<filter id="shadow" x="-20%" y="-20%" width="140%" height="150%"><feGaussianBlur stdDeviation="16"/></filter>
<clipPath id="screen"><rect width="{W}" height="{H}" rx="12"/></clipPath>
<g id="wp">{scene}</g>
</defs>
<g clip-path="url(#screen)">
<use href="#wp"/>
{mist}
<use href="#front"/>
{menubar()}
{about(44, 60, 290, 266)}
{terminal(388, 128, 452, 198)}
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="11.5" fill="none" stroke="#000" stroke-opacity=".35"/>
</svg>
'''


# ---------------------------------------------------------------- plan terminal

def plan():
    wx, wy, tw = 92, 14, 696
    session = [
        ("cat ~/.plan", [[(line, "#f2f4f5" if i == 0 else "#c3cad1", 0)] for i, line in enumerate(PLAN)]),
    ]
    lines = sum(1 + len(rows) for _, rows in session) + 1
    th = 53 + (lines - 1) * LH + 20
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 {wy + th + 42}" width="880" height="{wy + th + 42}" role="img" aria-label="Terminal: what {esc(NAME)} builds">
<style>.ui{{font-family:{SANS}}}.mono{{font-family:{MONO}}}</style>
<defs>
<filter id="shadow" x="-10%" y="-10%" width="120%" height="140%"><feGaussianBlur stdDeviation="14"/></filter>
<clipPath id="win"><rect x="{wx}" y="{wy}" width="{tw}" height="{th}" rx="11"/></clipPath>
</defs>
<rect x="{wx}" y="{wy + 12}" width="{tw}" height="{th}" rx="11" fill="#000" opacity=".4" filter="url(#shadow)"/>
<g clip-path="url(#win)">
<rect x="{wx}" y="{wy}" width="{tw}" height="{th}" fill="#16191d"/>
<rect x="{wx}" y="{wy}" width="{tw}" height="28" fill="#2a2d32"/>
<path d="M{wx} {wy + 28.5}h{tw}" stroke="#000" stroke-opacity=".5"/>
</g>
{lights(wx + 18, wy + 14)}
<text x="{wx + tw / 2}" y="{wy + 18.5}" class="ui" font-size="12" font-weight="600" fill="#aab2ba" text-anchor="middle">rahul — -zsh — 88×{lines}</text>
{typed(wx + 16, wy + 53, session)}
<rect x="{wx + .5}" y="{wy + .5}" width="{tw - 1}" height="{th - 1}" rx="10.5" fill="none" stroke="#fff" stroke-opacity=".15"/>
</svg>
'''


# ---------------------------------------------------------------- finder

def finder():
    fw, row_h, bar, head, status = 832, 54, 50, 24, 26
    wx, wy = 24, 14
    fh = bar + head + row_h * len(STACK) + status
    total = sum(len(items) for _, items in STACK)
    y0 = wy + bar + head
    right = wx + fw
    rows = []
    for i, (folder, items) in enumerate(STACK):
        y = y0 + i * row_h
        mid = y + row_h / 2
        if i % 2:
            rows.append(f'<rect x="{wx}" y="{y}" width="{fw}" height="{row_h}" fill="#fff" opacity=".035"/>')
        rows.append(
            f'<path d="M{wx + 16} {mid - 4}l4 4-4 4" fill="none" stroke="#8b9198" stroke-width="1.6" '
            f'stroke-linecap="round" stroke-linejoin="round"/>'
            f'<g transform="translate({wx + 32} {mid - 8.5})">'
            '<path d="M0 2.4C0 1.1 1.1 0 2.4 0h4.2c.6 0 1.2.2 1.6.7l1 1h8.4C18.9 1.7 20 2.8 20 4.1v10.5'
            'c0 1.3-1.1 2.4-2.4 2.4H2.4C1.1 17 0 15.9 0 14.6z" fill="#2f8fe8"/>'
            '<path d="M0 5.8c0-1 .8-1.8 1.8-1.8h16.4c1 0 1.8.8 1.8 1.8v8.8c0 1.3-1.1 2.4-2.4 2.4H2.4'
            'C1.1 17 0 15.9 0 14.6z" fill="#5cb4ff"/></g>'
            f'<text x="{wx + 62}" y="{mid + 4.5}" class="ui" font-size="13" fill="#e8eaec">{esc(folder)}</text>'
            f'<text x="{right - 20}" y="{mid + 4}" class="ui" font-size="12" fill="#8b9198" '
            f'text-anchor="end">{len(items)} items</text>'
        )
        rows += [icon(name, wx + 196 + k * 46, y + 9, 36) for k, name in enumerate(items)]
    hy = wy + bar
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 880 {wy + fh + 42}" width="880" height="{wy + fh + 42}" role="img" aria-label="Finder window listing the tech stack">
<style>.ui{{font-family:{SANS}}}</style>
<defs>
<filter id="shadow" x="-10%" y="-10%" width="120%" height="130%"><feGaussianBlur stdDeviation="14"/></filter>
<clipPath id="win"><rect x="{wx}" y="{wy}" width="{fw}" height="{fh}" rx="11"/></clipPath>
</defs>
<rect x="{wx}" y="{wy + 12}" width="{fw}" height="{fh}" rx="11" fill="#000" opacity=".4" filter="url(#shadow)"/>
<g clip-path="url(#win)">
<rect x="{wx}" y="{wy}" width="{fw}" height="{fh}" fill="#1d1f23"/>
<rect x="{wx}" y="{wy}" width="{fw}" height="{bar}" fill="#2a2d32"/>
<rect x="{wx}" y="{wy + fh - status}" width="{fw}" height="{status}" fill="#25282c"/>
<path d="M{wx} {hy + .5}h{fw}M{wx} {hy + head + .5}h{fw}M{wx} {wy + fh - status + .5}h{fw}" stroke="#000" stroke-opacity=".45"/>
<path d="M{wx + 184} {hy + 5}v14M{right - 96} {hy + 5}v14" stroke="#fff" stroke-opacity=".1"/>
{"".join(rows)}
</g>
{lights(wx + 20, wy + 25)}
<g fill="none" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
<path d="M{wx + 96} {wy + 19}l-6 6 6 6" stroke="#b9bfc5"/><path d="M{wx + 118} {wy + 19}l6 6-6 6" stroke="#5d646b"/></g>
<text x="{wx + 146}" y="{wy + 30}" class="ui" font-size="14" font-weight="700" fill="#eef0f2">stack</text>
<g transform="translate({right - 286} {wy + 13})">
<rect width="90" height="24" rx="6" fill="#fff" opacity=".06"/><rect x="30" width="30" height="24" rx="6" fill="#fff" opacity=".14"/>
<g fill="#b9bfc5"><rect x="9" y="6.5" width="5" height="5" rx="1.2"/><rect x="16" y="6.5" width="5" height="5" rx="1.2"/><rect x="9" y="13.5" width="5" height="5" rx="1.2"/><rect x="16" y="13.5" width="5" height="5" rx="1.2"/>
<rect x="38" y="7" width="14" height="1.8" rx=".9"/><rect x="38" y="11.1" width="14" height="1.8" rx=".9"/><rect x="38" y="15.2" width="14" height="1.8" rx=".9"/>
<rect x="68" y="6.5" width="3.6" height="11" rx="1"/><rect x="73.2" y="6.5" width="3.6" height="11" rx="1"/><rect x="78.4" y="6.5" width="3.6" height="11" rx="1"/></g></g>
<g transform="translate({right - 180} {wy + 13})">
<rect width="164" height="24" rx="6" fill="#fff" opacity=".07"/>
<circle cx="13" cy="11" r="4.2" fill="none" stroke="#8b9198" stroke-width="1.5"/><path d="M16.2 14.2l3.4 3.4" stroke="#8b9198" stroke-width="1.5" stroke-linecap="round"/>
<text x="27" y="16.2" class="ui" font-size="12.5" fill="#8b9198">Search</text></g>
<g class="ui" font-size="11.5" font-weight="600" fill="#9aa0a6">
<text x="{wx + 32}" y="{hy + 16}">Name</text><text x="{wx + 196}" y="{hy + 16}">Contents</text>
<text x="{right - 20}" y="{hy + 16}" text-anchor="end">Size</text></g>
<text x="{wx + fw / 2}" y="{wy + fh - 9}" class="ui" font-size="11.5" fill="#9aa0a6" text-anchor="middle">{len(STACK)} folders, {total} items</text>
<rect x="{wx + .5}" y="{wy + .5}" width="{fw - 1}" height="{fh - 1}" rx="10.5" fill="none" stroke="#fff" stroke-opacity=".15"/>
</svg>
'''


# ---------------------------------------------------------------- dock

DOCK_APPS = {
    "portfolio": (
        '<linearGradient id="t" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fdfdfd"/>'
        '<stop offset="1" stop-color="#d5dade"/></linearGradient>'
        '<linearGradient id="c" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3ccbff"/>'
        '<stop offset="1" stop-color="#1566e0"/></linearGradient>'
        '<rect width="48" height="48" rx="11" fill="url(#t)"/><circle cx="24" cy="24" r="17.5" fill="url(#c)"/>'
        '<g stroke="#fff" stroke-opacity=".75" stroke-width="1.2" stroke-linecap="round">'
        '<path d="M24 8.6v2.6M24 36.8v2.6M8.6 24h2.6M36.8 24h2.6"/></g>'
        '<path d="M34.4 13.6L26.2 26.2 21.8 21.8z" fill="#ff4b3e"/>'
        '<path d="M13.6 34.4L26.2 26.2 21.8 21.8z" fill="#fff"/>'
    ),
    "linkedin": (
        '<rect width="48" height="48" rx="11" fill="#0a66c2"/>'
        '<circle cx="15.2" cy="14.6" r="3.3" fill="#fff"/><rect x="12.4" y="20.4" width="5.6" height="15.6" fill="#fff"/>'
        '<path d="M21.6 20.4h5.3v2.3c.9-1.6 2.9-2.8 5.5-2.8 4.3 0 6.4 2.7 6.4 7.4V36h-5.6v-7.6'
        'c0-2.3-.9-3.6-2.8-3.6-2 0-3.2 1.4-3.2 3.9V36h-5.6z" fill="#fff"/>'
    ),
    "mail": (
        '<linearGradient id="m" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5fd0ff"/>'
        '<stop offset="1" stop-color="#1a72ee"/></linearGradient>'
        '<rect width="48" height="48" rx="11" fill="url(#m)"/>'
        '<rect x="9" y="14" width="30" height="20" rx="3.4" fill="#fff"/>'
        '<path d="M10.6 16.4L24 26.6l13.4-10.2" fill="none" stroke="#2a86f0" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round"/>'
    ),
    "instagram": (
        '<radialGradient id="i" cx=".28" cy="1.05" r="1.25"><stop offset="0" stop-color="#feda75"/>'
        '<stop offset=".25" stop-color="#fa7e1e"/><stop offset=".5" stop-color="#d62976"/>'
        '<stop offset=".75" stop-color="#962fbf"/><stop offset="1" stop-color="#4f5bd5"/></radialGradient>'
        '<rect width="48" height="48" rx="11" fill="url(#i)"/>'
        '<g fill="none" stroke="#fff" stroke-width="3"><rect x="11.5" y="11.5" width="25" height="25" rx="7.5"/>'
        '<circle cx="24" cy="24" r="6"/></g><circle cx="31.4" cy="16.6" r="1.8" fill="#fff"/>'
    ),
}
DOCK_H, DOCK_TILE, DOCK_CAP = 78, 68, 14
DOCK_SHELF = 'y="6.5" height="65" rx="19" fill="#7c8791" fill-opacity=".2" stroke="#8a96a0" stroke-opacity=".45"'


def dock_slice(width, shelf_x, shelf_w, body=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {DOCK_H}" width="{width}" '
            f'height="{DOCK_H}"><rect x="{shelf_x}" width="{shelf_w}" {DOCK_SHELF}/>{body}</svg>\n')


def dock():
    files = {
        "dock-left.svg": dock_slice(DOCK_CAP, 0.5, 80),
        "dock-right.svg": dock_slice(DOCK_CAP, DOCK_CAP - 80.5, 80),
    }
    for name, art in DOCK_APPS.items():
        body = (f'<g transform="translate(10 12)">{art}'
                '<rect x=".5" y=".5" width="47" height="47" rx="10.5" fill="none" stroke="#fff" stroke-opacity=".18"/></g>'
                '<circle cx="34" cy="66" r="1.7" fill="#8a96a0"/>')
        files[f"dock-{name}.svg"] = dock_slice(DOCK_TILE, -40, DOCK_TILE + 80, body)
    return files


def main():
    ASSETS.mkdir(exist_ok=True)
    files = {"desktop.svg": desktop(), "plan.svg": plan(), "stack.svg": finder(), **dock()}
    for name, content in files.items():
        (ASSETS / name).write_text(content)
        print(f"{name:20} {len(content) / 1024:6.1f} KB")


if __name__ == "__main__":
    main()
