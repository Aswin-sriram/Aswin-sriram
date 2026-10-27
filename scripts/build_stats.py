"""Build an animated contribution-stats card from GitHub's GraphQL API.

Counts match the public contribution calendar, so private contributions are
included when "Include private contributions on my profile" is turned on.

Usage:  GITHUB_TOKEN=... python scripts/build_stats.py <username> <output.svg>
"""
import datetime as dt
import json
import os
import sys
import urllib.request

CYAN, GREEN, TEXT, MUTED, BG, BORDER = "#22d3ee", "#34d399", "#e6edf3", "#8b949e", "#0a0f1a", "#1f2a3a"
SANS = "'Segoe UI', Ubuntu, 'Helvetica Neue', Arial, sans-serif"
MONO = "'JetBrains Mono', 'SFMono-Regular', Consolas, Menlo, monospace"


def gql(query, token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query}).encode(),
        headers={"Authorization": f"bearer {token}", "User-Agent": "profile-stats"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        body = json.load(r)
    if "errors" in body:
        raise SystemExit(body["errors"])
    return body["data"]


def fetch_days(user, token):
    created = gql(f'{{user(login:"{user}"){{createdAt}}}}', token)["user"]["createdAt"]
    today = dt.datetime.now(dt.timezone.utc).date()
    parts = []
    for year in range(int(created[:4]), today.year + 1):
        parts.append(
            f'y{year}: contributionsCollection(from:"{year}-01-01T00:00:00Z", to:"{year}-12-31T23:59:59Z")'
            "{contributionCalendar{weeks{contributionDays{date contributionCount}}}}"
        )
    data = gql(f'{{user(login:"{user}"){{{" ".join(parts)}}}}}', token)["user"]
    days = {}
    for col in data.values():
        for w in col["contributionCalendar"]["weeks"]:
            for d in w["contributionDays"]:
                day = dt.date.fromisoformat(d["date"])
                if day <= today:
                    days[day] = d["contributionCount"]
    return dict(sorted(days.items())), today


def streaks(days, today):
    dates = list(days)
    # current streak: count back from today (or yesterday if nothing yet today)
    cur, d = 0, today if days.get(today, 0) else today - dt.timedelta(days=1)
    cur_end = d
    while days.get(d, 0) > 0:
        cur, d = cur + 1, d - dt.timedelta(days=1)
    cur_start = d + dt.timedelta(days=1)
    best, best_range, run, start = 0, None, 0, None
    for day in dates:
        if days[day] > 0:
            run, start = run + 1, start or day
            if run > best:
                best, best_range = run, (start, day)
        else:
            run, start = 0, None
    return cur, (cur_start, cur_end), best, best_range


def fmt(d):
    return d.strftime("%b %d, %Y").replace(" 0", " ")


def render(user, days, today):
    total = sum(days.values())
    year_ago = today - dt.timedelta(days=365)
    last_year = sum(c for d, c in days.items() if d > year_ago)
    active = sum(1 for d, c in days.items() if d > year_ago and c > 0)
    cur, cur_rng, best, best_rng = streaks(days, today)
    first = next((d for d, c in days.items() if c > 0), today)

    # 26-week mini heatmap
    weeks = 26
    start = today - dt.timedelta(days=(today.weekday() + 1) % 7 + 7 * (weeks - 1))  # a Sunday
    peak = max([days.get(start + dt.timedelta(days=i), 0) for i in range(weeks * 7)] + [1])
    cells = []
    for i in range(weeks * 7):
        day = start + dt.timedelta(days=i)
        if day > today:
            continue
        c = days.get(day, 0)
        x, y = 720 + (i // 7) * 16, 214 + (i % 7) * 16
        if c == 0:
            cells.append(f'<rect x="{x}" y="{y}" width="12" height="12" rx="3" fill="#161b22"/>')
        else:
            op = 0.35 + 0.65 * min(1, c / peak)
            col = GREEN if c / peak > 0.5 else CYAN
            delay = 0.6 + (i // 7) * 0.03
            cells.append(
                f'<rect class="pop" style="animation-delay:{delay:.2f}s" x="{x}" y="{y}" width="12" height="12" rx="3" fill="{col}" fill-opacity="{op:.2f}"/>'
            )

    circ = 2 * 3.14159 * 62
    ring = min(1.0, cur / max(best, 1)) if cur else 0.04

    def stat(x, big, label, sub, delay):
        return (
            f'<g class="fade" style="animation-delay:{delay}s">'
            f'<text x="{x}" y="128" text-anchor="middle" class="sans" font-size="46" font-weight="800" fill="url(#g)">{big}</text>'
            f'<text x="{x}" y="162" text-anchor="middle" class="sans" font-size="18" fill="{TEXT}">{label}</text>'
            f'<text x="{x}" y="188" text-anchor="middle" class="mono" font-size="13" fill="{MUTED}">{sub}</text></g>'
        )

    best_sub = f"{fmt(best_rng[0])} – {fmt(best_rng[1])}" if best_rng else "—"
    cur_sub = f"{fmt(cur_rng[0])} – {fmt(cur_rng[1])}" if cur else "start one today"
    updated = dt.datetime.now(dt.timezone.utc).strftime("%b %d, %Y %H:%M UTC")

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="360" viewBox="0 0 1200 360" role="img" aria-label="{total} total contributions, {cur} day current streak, {best} day longest streak">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{CYAN}"/><stop offset="50%" stop-color="{GREEN}"/><stop offset="100%" stop-color="{CYAN}"/>
      <animateTransform attributeName="gradientTransform" type="translate" from="-1 0" to="1 0" dur="6s" repeatCount="indefinite"/>
    </linearGradient>
    <linearGradient id="b" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{CYAN}" stop-opacity=".5"/><stop offset="50%" stop-color="{BORDER}"/><stop offset="100%" stop-color="{GREEN}" stop-opacity=".5"/>
    </linearGradient>
    <pattern id="p" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="{CYAN}" stroke-opacity=".05"/></pattern>
    <filter id="f" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="55"/></filter>
    <clipPath id="c"><rect x="1" y="1" width="1198" height="358" rx="20"/></clipPath>
  </defs>
  <style>
    .sans {{ font-family: {SANS}; }} .mono {{ font-family: {MONO}; }}
    .fade {{ opacity: 0; animation: up .8s ease-out forwards; }}
    @keyframes up {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: none; }} }}
    .pop {{ opacity: 0; animation: pop .4s ease-out forwards; }}
    @keyframes pop {{ to {{ opacity: 1; }} }}
    .ring {{ stroke-dasharray: {circ:.1f}; stroke-dashoffset: {circ:.1f}; animation: draw 1.6s .4s ease-out forwards; }}
    @keyframes draw {{ to {{ stroke-dashoffset: {circ * (1 - ring):.1f}; }} }}
    .flame {{ animation: flick 1.4s ease-in-out infinite; transform-box: fill-box; transform-origin: bottom; }}
    @keyframes flick {{ 0%,100% {{ transform: scale(1); }} 50% {{ transform: scale(1.12) rotate(-3deg); }} }}
  </style>
  <g clip-path="url(#c)">
    <rect width="1200" height="360" fill="{BG}"/><rect width="1200" height="360" fill="url(#p)"/>
    <circle cx="380" cy="300" r="170" fill="{CYAN}" opacity=".12" filter="url(#f)"/>
  </g>
  <rect x="1" y="1" width="1198" height="358" rx="20" fill="none" stroke="url(#b)" stroke-width="1.5"/>

  <text x="48" y="54" class="mono fade" font-size="14" fill="{CYAN}" letter-spacing="2">CONTRIBUTIONS · INCLUDING PRIVATE WORK</text>

  {stat(150, f"{total:,}", "Total contributions", f"since {fmt(first)}", .1)}

  <g class="fade" style="animation-delay:.25s">
    <circle cx="390" cy="128" r="62" fill="none" stroke="#161b22" stroke-width="9"/>
    <circle class="ring" cx="390" cy="128" r="62" fill="none" stroke="url(#g)" stroke-width="9" stroke-linecap="round" transform="rotate(-90 390 128)"/>
    <path class="flame" d="M390 50c6 8 10 13 10 20a10 10 0 0 1-20 0c0-5 3-8 6-11 0 4 2 6 4 6 0-5-2-9 0-15z" fill="{GREEN}"/>
    <text x="390" y="144" text-anchor="middle" class="sans" font-size="46" font-weight="800" fill="{TEXT}">{cur}</text>
    <text x="390" y="226" text-anchor="middle" class="sans" font-size="18" font-weight="700" fill="{CYAN}">Current streak</text>
    <text x="390" y="252" text-anchor="middle" class="mono" font-size="13" fill="{MUTED}">{cur_sub}</text>
  </g>

  {stat(600, f"{best}", "Longest streak (days)", best_sub, .4)}

  <g class="fade" style="animation-delay:.55s">
    <text x="48" y="292" class="mono" font-size="15" fill="{MUTED}"><tspan fill="{GREEN}" font-weight="700">{last_year:,}</tspan> contributions in the last year  ·  <tspan fill="{GREEN}" font-weight="700">{active}</tspan> active days</text>
    <text x="48" y="324" class="mono" font-size="12" fill="#484f58">updated {updated}</text>
  </g>

  <text x="720" y="54" class="mono fade" font-size="14" fill="{CYAN}" letter-spacing="2">LAST 6 MONTHS</text>
  <text x="720" y="96" class="sans fade" font-size="30" font-weight="800" fill="url(#g)">{sum(days.get(start + dt.timedelta(days=i), 0) for i in range(weeks * 7)):,}</text>
  <text x="720" y="122" class="sans fade" font-size="16" fill="{MUTED}">contributions in 26 weeks</text>
  <g transform="translate(0,-60)">{''.join(cells)}</g>
</svg>
"""


if __name__ == "__main__":
    user, out = sys.argv[1], sys.argv[2]
    days, today = fetch_days(user, os.environ["GITHUB_TOKEN"])
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(render(user, days, today))
    print(f"wrote {out}: {sum(days.values())} total contributions")
