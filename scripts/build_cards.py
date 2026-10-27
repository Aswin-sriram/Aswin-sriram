"""Generate the animated SVG section cards used by the profile README.

Run from the repo root:  python scripts/build_cards.py
Edit the content dictionaries below, re-run, commit the files in assets/.
"""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "assets"

BG, PANEL, BORDER = "#0a0f1a", "#0d1424", "#1f2a3a"
CYAN, GREEN, ORANGE = "#22d3ee", "#34d399", "#f0883e"
TEXT, MUTED = "#e6edf3", "#8b949e"
SANS = "'Segoe UI', Ubuntu, 'Helvetica Neue', Arial, sans-serif"
MONO = "'JetBrains Mono', 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace"

STYLE = f"""
  <style>
    .sans {{ font-family: {SANS}; }}
    .mono {{ font-family: {MONO}; }}
    .fade {{ opacity: 0; animation: fadeUp .8s ease-out forwards; }}
    @keyframes fadeUp {{ from {{ opacity: 0; transform: translateY(12px); }} to {{ opacity: 1; transform: none; }} }}
    .orb {{ animation: drift 14s ease-in-out infinite alternate; }}
    @keyframes drift {{ to {{ transform: translate(90px, 30px); }} }}
    .pulse {{ animation: pulse 1.8s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }}
    @keyframes pulse {{ 0%,100% {{ opacity: 1; transform: scale(1); }} 50% {{ opacity: .35; transform: scale(1.7); }} }}
    .cursor {{ animation: blink 1s steps(1) infinite; }}
    @keyframes blink {{ 50% {{ opacity: 0; }} }}
  </style>"""


def defs(uid, w, h):
    return f"""
  <defs>
    <linearGradient id="g{uid}" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{CYAN}"/><stop offset="50%" stop-color="{GREEN}"/><stop offset="100%" stop-color="{CYAN}"/>
      <animateTransform attributeName="gradientTransform" type="translate" from="-1 0" to="1 0" dur="6s" repeatCount="indefinite"/>
    </linearGradient>
    <linearGradient id="b{uid}" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{CYAN}" stop-opacity=".5"/><stop offset="50%" stop-color="{BORDER}"/><stop offset="100%" stop-color="{GREEN}" stop-opacity=".5"/>
    </linearGradient>
    <linearGradient id="s{uid}" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{CYAN}" stop-opacity="0"/><stop offset="50%" stop-color="{CYAN}" stop-opacity=".9"/><stop offset="100%" stop-color="{CYAN}" stop-opacity="0"/>
    </linearGradient>
    <pattern id="p{uid}" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M40 0H0V40" fill="none" stroke="{CYAN}" stroke-opacity=".05"/>
    </pattern>
    <filter id="f{uid}" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="55"/></filter>
    <clipPath id="c{uid}"><rect x="1" y="1" width="{w-2}" height="{h-2}" rx="20"/></clipPath>
  </defs>"""


def card(uid, w, h, body, orb=(0.85, 0.2), label=""):
    """Wrap body in the shared card frame: grid, drifting glow, gradient border, light sweep."""
    ox, oy = w * orb[0], h * orb[1]
    sweep = f"""
    <rect x="-300" y="0" width="300" height="2" fill="url(#s{uid})">
      <animate attributeName="x" from="-300" to="{w}" dur="5s" repeatCount="indefinite"/>
    </rect>"""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(label)}">{defs(uid, w, h)}{STYLE}
  <g clip-path="url(#c{uid})">
    <rect width="{w}" height="{h}" fill="{BG}"/>
    <rect width="{w}" height="{h}" fill="url(#p{uid})"/>
    <circle class="orb" cx="{ox:.0f}" cy="{oy:.0f}" r="{min(w, h) * 0.45:.0f}" fill="{GREEN}" opacity=".16" filter="url(#f{uid})"/>{sweep}
  </g>
  <rect x="1" y="1" width="{w-2}" height="{h-2}" rx="20" fill="none" stroke="url(#b{uid})" stroke-width="1.5"/>
{body}
</svg>
"""


def wrap(text, size, width, ratio=0.5):
    limit = max(10, int(width / (size * ratio)))
    lines, cur = [], ""
    for word in text.split():
        if cur and len(cur) + 1 + len(word) > limit:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}".strip()
    if cur:
        lines.append(cur)
    return lines


def chip_w(t, size=16):
    return len(t) * size * 0.6 + 28


def chips(items, x, y, max_x, size=16, delay=0.0, step=0.06, color=CYAN, gap=10, row_h=40):
    out, cx, cy = [], x, y
    for i, t in enumerate(items):
        w = chip_w(t, size)
        if cx + w > max_x:
            cx, cy = x, cy + row_h
        out.append(
            f'  <g class="fade" style="animation-delay:{delay + i * step:.2f}s">'
            f'<rect x="{cx:.0f}" y="{cy}" width="{w:.0f}" height="30" rx="15" fill="{color}" fill-opacity=".08" stroke="{color}" stroke-opacity=".35"/>'
            f'<text x="{cx + w / 2:.0f}" y="{cy + 20}" text-anchor="middle" class="mono" font-size="{size}" fill="{TEXT}">{escape(t)}</text></g>'
        )
        cx += w + gap
    return "\n".join(out), cy + row_h


def title(tag, heading, x=48, y=58, uid="t", delay=0.0):
    return (
        f'  <text x="{x}" y="{y}" class="mono fade" style="animation-delay:{delay}s" font-size="16" fill="{CYAN}" letter-spacing="2">// {escape(tag)}</text>\n'
        f'  <text x="{x}" y="{y + 42}" class="sans fade" style="animation-delay:{delay + .1}s" font-size="34" font-weight="700" fill="{TEXT}">{escape(heading)}</text>'
    )


# ───────────────────────── content ─────────────────────────

IMPACT = [
    ("PERFORMANCE", "~80%", "lower real-time latency", "5–6 s → 0.6–1 s"),
    ("PRODUCT", "700+", "Play Store downloads", "HIT Learn app"),
    ("RESEARCH", "IEEE", "paper published", "I-SMAC 2025 · Nepal"),
    ("EDUCATION", "B.Tech", "Computer Science", "Amrita · 2026"),
]

ABOUT = (
    "I'm a Software Engineer from Coimbatore, India, with about a year of production experience "
    "building backend services, real-time APIs and applied-AI workflows for a live SaaS platform. "
    "I like profiling slow systems until they're fast, keeping production healthy, and shipping "
    "features across the whole stack."
)
ABOUT_YAML = [
    ("role", "Software Engineer"),
    ("company", "Home Ideas Technologies"),
    ("focus", "Backend · Voice AI · RAG"),
    ("research", "IEEE I-SMAC 2025"),
    ("open_to", "SWE roles"),
    ("relocate", "Bengaluru · Hyderabad · Pune"),
]

EXPERIENCE = {
    "role": "Software Engineer",
    "company": "Home Ideas Technologies",
    "when": "NOV 2025 — PRESENT",
    "where": "Coimbatore, India",
    "bullets": [
        "Build and maintain backend services and REST APIs for VIGOE, a real-time voice & chat SaaS platform, integrating WhatsApp, Gemini and OpenAI.",
        "Cut real-time response latency from ~5–6 s to 0.6–1 s (~80%) by profiling and optimizing response handling, backend logic and API flows.",
        "Built a BM25-based retrieval pipeline over the platform's media data and connected RAG/LLM pipelines to the Gemini and OpenAI APIs.",
        "Built real-time voice over WebSockets for HIT Learn (700+ Play Store downloads) and fixed production bugs like microphone echo and interruptions.",
        "Own features end to end with Docker, Git and Linux on AWS, working through code reviews in a 7-developer team.",
    ],
    "stack": ["Node.js", "TypeScript", "Python", "WebSockets", "Gemini", "OpenAI", "AWS", "Docker"],
}

STACK = [
    ("LANGUAGES", ["Python", "TypeScript", "JavaScript", "Java", "C++", "SQL"]),
    ("BACKEND", ["FastAPI", "Node.js", "Express", "REST APIs", "WebSockets", "Microservices", "Redis"]),
    ("WEB & MOBILE", ["React", "React Native", "Tailwind CSS", "Supabase"]),
    ("CLOUD & DEVOPS", ["AWS", "GCP", "Azure", "Docker", "Linux", "Git", "CI/CD"]),
    ("APPLIED AI", ["LLMs", "RAG", "Gemini API", "OpenAI API", "Voice AI", "BM25", "MediaPipe", "LSTM"]),
]

PROJECTS = [
    ("vigoe", "PRODUCTION · VOICE AI SAAS", "VIGOE",
     "Backend services and APIs for a real-time voice & chat platform with WhatsApp, Gemini and OpenAI integrations.",
     "~80% lower latency", ["Node.js", "WebSockets", "Gemini", "AWS"]),
    ("hitlearn", "PRODUCTION · MOBILE APP", "HIT Learn",
     "AI-powered education app. Built mobile and backend features plus real-time AI voice over WebSockets.",
     "700+ downloads", ["React Native", "TypeScript", "Node.js"]),
    ("isl", "FINAL-YEAR PROJECT · CV", "Sign Language Translation",
     "Indian Sign Language recognition: hand landmarks modeled over time and mapped to HamNoSys/SiGML for a 3D avatar.",
     "3D avatar output", ["Python", "MediaPipe", "LSTM"]),
    ("climastyle", "RESEARCH · IEEE I-SMAC 2025", "ClimaStyle",
     "Climate-aware visual try-on using prompt-based segmentation. Published and presented in Nepal, Oct 2025.",
     "IEEE published", ["Python", "Computer Vision"]),
    ("gamelab", "OPEN SOURCE · EDTECH", "Build-a-Game Lab",
     "Learn-to-code lab: students type the key code of 10 classic games, run them in the browser and share a link.",
     "Live demo ↗", ["JavaScript", "HTML", "GitHub Pages"]),
    ("omagentz", "CLIENT WEBSITE", "Om Canvassing Agentz",
     "Responsive business website for a wholesale grain supplier in Trichy, Tamil Nadu.",
     "Shipped", ["React", "TypeScript", "Tailwind", "Supabase"]),
]

RESEARCH = {
    "paper": "ClimaStyle: Climate-Aware Visual Try-On with Prompt-Based Segmentation",
    "venue": "9th Int'l Conference on I-SMAC (IEEE) · Nepal · Oct 2025",
    "degree": "B.Tech, Computer Science & Engineering",
    "school": "Amrita Vishwa Vidyapeetham, Coimbatore · 2026",
    "certs": [
        ("Microsoft Azure", "AI & Cloud training program"),
        ("Google Cloud", "Agentic AI Day"),
        ("Infosys Springboard", "Deep Learning, NLP"),
        ("BCG X", "GenAI Job Simulation"),
    ],
}

CONNECT = [
    ("linkedin", "LinkedIn", "/in/aswinsrirams", CYAN),
    ("email", "Email", "aswinsriram268@gmail.com", GREEN),
    ("demo", "Live demo", "Build-a-Game Lab", CYAN),
]


# ───────────────────────── builders ─────────────────────────

def build_impact():
    w, h, gap = 1200, 190, 24
    tw = (w - 3 * gap) / 4
    parts = []
    for i, (tag, big, l1, l2) in enumerate(IMPACT):
        x = i * (tw + gap)
        d = 0.1 + i * 0.15
        parts.append(f"""  <g class="fade" style="animation-delay:{d:.2f}s">
    <rect x="{x + 1:.0f}" y="1" width="{tw - 2:.0f}" height="{h - 2}" rx="18" fill="{BG}" stroke="url(#bi)" stroke-width="1.5"/>
    <rect x="{x + 1:.0f}" y="1" width="{tw - 2:.0f}" height="{h - 2}" rx="18" fill="url(#pi)"/>
    <text x="{x + 28:.0f}" y="44" class="mono" font-size="14" fill="{CYAN}" letter-spacing="2">{escape(tag)}</text>
    <text x="{x + 26:.0f}" y="104" class="sans" font-size="54" font-weight="800" fill="url(#gi)">{escape(big)}</text>
    <text x="{x + 28:.0f}" y="138" class="sans" font-size="19" fill="{TEXT}">{escape(l1)}</text>
    <text x="{x + 28:.0f}" y="166" class="mono" font-size="15" fill="{MUTED}">{escape(l2)}</text>
  </g>""")
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="Impact highlights">{defs("i", w, h)}{STYLE}
{chr(10).join(parts)}
</svg>
"""
    (OUT / "impact.svg").write_text(svg, encoding="utf-8")


def build_about():
    lines = wrap(ABOUT, 21, 560)
    w, h = 1200, max(330, 150 + len(lines) * 32 + 20)
    body = [title("about", "Hi, I'm Aswin 👋")]
    for i, line in enumerate(lines):
        body.append(f'  <text x="48" y="{150 + i * 32}" class="sans fade" style="animation-delay:{.3 + i * .08:.2f}s" font-size="21" fill="#c9d1d9">{escape(line)}</text>')
    # terminal window
    tx, ty, tw, th = 660, 40, 500, 250
    body.append(f"""  <g class="fade" style="animation-delay:.4s">
    <rect x="{tx}" y="{ty}" width="{tw}" height="{th}" rx="14" fill="{PANEL}" stroke="{BORDER}"/>
    <circle cx="{tx + 22}" cy="{ty + 22}" r="6" fill="#ff5f56"/><circle cx="{tx + 42}" cy="{ty + 22}" r="6" fill="#ffbd2e"/><circle cx="{tx + 62}" cy="{ty + 22}" r="6" fill="#27c93f"/>
    <text x="{tx + tw / 2}" y="{ty + 27}" text-anchor="middle" class="mono" font-size="13" fill="{MUTED}">aswin.yaml</text>
    <line x1="{tx}" y1="{ty + 42}" x2="{tx + tw}" y2="{ty + 42}" stroke="{BORDER}"/>
  </g>""")
    for i, (k, v) in enumerate(ABOUT_YAML):
        d = 0.8 + i * 0.25
        body.append(
            f'  <text x="{tx + 24}" y="{ty + 78 + i * 29}" class="mono fade" style="animation-delay:{d:.2f}s" font-size="16">'
            f'<tspan fill="{GREEN}">{escape(k)}</tspan><tspan fill="{MUTED}">: </tspan><tspan fill="{TEXT}">{escape(v)}</tspan></text>'
        )
    last_y = ty + 78 + len(ABOUT_YAML) * 29
    body.append(f'  <rect class="cursor" x="{tx + 24}" y="{last_y - 14}" width="9" height="18" fill="{CYAN}"/>')
    (OUT / "about.svg").write_text(card("a", w, h, "\n".join(body), orb=(0.15, 0.9), label="About Aswin"), encoding="utf-8")


def build_experience():
    e = EXPERIENCE
    w = 1200
    lines_per = [wrap(b, 20, 1000) for b in e["bullets"]]
    bullets_h = sum(len(l) * 28 + 14 for l in lines_per)
    h = 230 + bullets_h + 70
    body = [title("experience", e["role"])]
    body.append(f'  <text x="48" y="140" class="sans fade" style="animation-delay:.2s" font-size="22" font-weight="600" fill="{GREEN}">{escape(e["company"])}</text>')
    pw = chip_w(e["when"], 15) + 20
    body.append(f"""  <g class="fade" style="animation-delay:.2s">
    <rect x="{w - 48 - pw:.0f}" y="40" width="{pw:.0f}" height="34" rx="17" fill="{GREEN}" fill-opacity=".1" stroke="{GREEN}" stroke-opacity=".45"/>
    <circle class="pulse" cx="{w - 48 - pw + 20:.0f}" cy="57" r="5" fill="{GREEN}"/>
    <text x="{w - 48 - pw + 34:.0f}" y="62" class="mono" font-size="15" font-weight="600" fill="{GREEN}">{e["when"]}</text>
    <text x="{w - 48}" y="104" text-anchor="end" class="mono" font-size="15" fill="{MUTED}">{escape(e["where"])}</text>
  </g>""")
    # timeline
    y = 190
    body.append(f'  <line x1="62" y1="{y - 8}" x2="62" y2="{y + bullets_h - 20}" stroke="{BORDER}" stroke-width="2"/>')
    for i, lines in enumerate(lines_per):
        d = 0.35 + i * 0.15
        body.append(f'  <g class="fade" style="animation-delay:{d:.2f}s"><circle cx="62" cy="{y - 6}" r="6" fill="{BG}" stroke="{CYAN}" stroke-width="2"/>')
        for j, line in enumerate(lines):
            body.append(f'    <text x="92" y="{y + j * 28}" class="sans" font-size="20" fill="#c9d1d9">{escape(line)}</text>')
        body.append("  </g>")
        y += len(lines) * 28 + 14
    chip_svg, _ = chips(e["stack"], 92, y + 6, w - 48, delay=1.2)
    body.append(chip_svg)
    (OUT / "experience.svg").write_text(card("e", w, h, "\n".join(body), orb=(0.9, 0.15), label="Experience"), encoding="utf-8")


def build_stack():
    w = 1200
    body = [title("tech stack", "Tools I build with")]
    y, delay = 150, 0.3
    rows = []
    for label, items in STACK:
        rows.append(f'  <text x="48" y="{y + 21}" class="mono fade" style="animation-delay:{delay:.2f}s" font-size="15" fill="{CYAN}" letter-spacing="1.5">{escape(label)}</text>')
        svg, y2 = chips(items, 270, y, w - 48, delay=delay, step=0.05)
        rows.append(svg)
        y, delay = y2 + 12, delay + 0.2
    body += rows
    h = y + 24
    (OUT / "stack.svg").write_text(card("k", w, h, "\n".join(body), orb=(0.1, 0.85), label="Tech stack"), encoding="utf-8")


def build_projects():
    w, h = 600, 330
    for i, (slug, tag, name, desc, metric, stack) in enumerate(PROJECTS):
        uid = f"p{i}"
        body = [
            f'  <text x="36" y="52" class="mono fade" font-size="13" fill="{CYAN}" letter-spacing="1.8">{escape(tag)}</text>',
            f'  <text x="34" y="100" class="sans fade" style="animation-delay:.1s" font-size="32" font-weight="800" fill="url(#g{uid})">{escape(name)}</text>',
        ]
        for j, line in enumerate(wrap(desc, 19, 520)):
            body.append(f'  <text x="36" y="{146 + j * 28}" class="sans fade" style="animation-delay:{.2 + j * .06:.2f}s" font-size="19" fill="#c9d1d9">{escape(line)}</text>')
        mw = chip_w(metric, 15) + 18
        body.append(f"""  <g class="fade" style="animation-delay:.4s">
    <rect x="{w - 36 - mw:.0f}" y="30" width="{mw:.0f}" height="32" rx="16" fill="{GREEN}" fill-opacity=".12" stroke="{GREEN}" stroke-opacity=".5"/>
    <circle class="pulse" cx="{w - 36 - mw + 18:.0f}" cy="46" r="4.5" fill="{GREEN}"/>
    <text x="{w - 36 - mw + 30:.0f}" y="51" class="mono" font-size="15" font-weight="600" fill="{GREEN}">{escape(metric)}</text>
  </g>""")
        chip_svg, _ = chips(stack, 36, h - 66, w - 36, size=15, delay=.5)
        body.append(chip_svg)
        (OUT / f"project-{slug}.svg").write_text(card(uid, w, h, "\n".join(body), orb=(0.95, 1.0), label=name), encoding="utf-8")


def build_research():
    r = RESEARCH
    w, h = 1200, 330
    body = [title("research &amp; education".replace("&amp;", "&"), "Research, education & certifications")]
    lx = 48
    body.append(f'  <text x="{lx}" y="160" class="mono fade" style="animation-delay:.2s" font-size="14" fill="{GREEN}" letter-spacing="2">PUBLICATION</text>')
    for j, line in enumerate(wrap(r["paper"], 21, 540)):
        body.append(f'  <text x="{lx}" y="{192 + j * 28}" class="sans fade" style="animation-delay:.3s" font-size="21" font-weight="600" fill="{TEXT}">{escape(line)}</text>')
    py = 192 + len(wrap(r["paper"], 21, 540)) * 28
    body.append(f'  <text x="{lx}" y="{py}" class="mono fade" style="animation-delay:.35s" font-size="15" fill="{MUTED}">{escape(r["venue"])}</text>')
    body.append(f'  <text x="{lx}" y="{py + 44}" class="mono fade" style="animation-delay:.4s" font-size="14" fill="{GREEN}" letter-spacing="2">EDUCATION</text>')
    body.append(f'  <text x="{lx}" y="{py + 74}" class="sans fade" style="animation-delay:.45s" font-size="21" font-weight="600" fill="{TEXT}">{escape(r["degree"])}</text>')
    body.append(f'  <text x="{lx}" y="{py + 100}" class="mono fade" style="animation-delay:.5s" font-size="15" fill="{MUTED}">{escape(r["school"])}</text>')
    # certificates column
    cx = 680
    body.append(f'  <text x="{cx}" y="160" class="mono fade" style="animation-delay:.2s" font-size="14" fill="{GREEN}" letter-spacing="2">CERTIFICATIONS</text>')
    for i, (org, what) in enumerate(r["certs"]):
        y = 178 + i * 36
        d = .35 + i * .12
        body.append(
            f'  <g class="fade" style="animation-delay:{d:.2f}s"><rect x="{cx}" y="{y}" width="472" height="30" rx="8" fill="{CYAN}" fill-opacity=".06" stroke="{BORDER}"/>'
            f'<circle cx="{cx + 16}" cy="{y + 15}" r="4" fill="{CYAN}"/>'
            f'<text x="{cx + 30}" y="{y + 21}" class="sans" font-size="17"><tspan fill="{TEXT}" font-weight="600">{escape(org)}</tspan><tspan fill="{MUTED}">  ·  {escape(what)}</tspan></text></g>'
        )
    hh = max(py + 130, 178 + len(r["certs"]) * 36 + 30)
    (OUT / "research.svg").write_text(card("r", w, hh, "\n".join(body), orb=(0.85, 0.9), label="Research and education"), encoding="utf-8")


def build_titles():
    for slug, tag, heading in [("projects", "projects", "Highlighted work"), ("activity", "github", "Activity & contributions")]:
        w, h = 1200, 120
        body = title(tag, heading, y=48)
        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(heading)}">{STYLE}
{body}
  <rect x="48" y="108" width="0" height="3" rx="1.5" fill="{CYAN}"><animate attributeName="width" from="0" to="120" dur="1s" begin=".3s" fill="freeze"/></rect>
</svg>
"""
        (OUT / f"title-{slug}.svg").write_text(svg, encoding="utf-8")


def build_connect():
    w, h = 380, 96
    for i, (slug, label, sub, color) in enumerate(CONNECT):
        uid = f"n{i}"
        body = (
            f'  <text x="32" y="44" class="sans" font-size="24" font-weight="700" fill="{TEXT}">{escape(label)}</text>\n'
            f'  <text x="32" y="72" class="mono" font-size="15" fill="{color}">{escape(sub)}</text>\n'
            f'  <text x="{w - 36}" y="58" text-anchor="end" class="sans" font-size="30" fill="{color}">↗'
            f'<animate attributeName="opacity" values="1;.4;1" dur="2s" repeatCount="indefinite"/></text>'
        )
        (OUT / f"connect-{slug}.svg").write_text(card(uid, w, h, body, orb=(1, .5), label=label), encoding="utf-8")


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    build_impact(); build_about(); build_experience(); build_stack()
    build_projects(); build_research(); build_titles(); build_connect()
    print("\n".join(sorted(p.name for p in OUT.glob("*.svg"))))
