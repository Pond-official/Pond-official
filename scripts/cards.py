"""Builders for the pictures on the profile. Each returns one SVG document."""
from __future__ import annotations

import random
from datetime import date

import art
import sprite
from canvas import Canvas, Clock, frames
from term import Term, cells, glyph, ink_box, pick, plain
from theme import mix, ramp

W = 840  # every card is 840 px wide; GitHub scales it to the column
M = 10  # room for the window shadow
BAR_H = 34
PAD = 24


# ------------------------------------------------------------------ helpers

def window(c: Canvas, P: dict, h: float, title: str) -> tuple[float, float]:
    """Draw the terminal window and return the content origin."""
    x, y, w = M, M, c.w - 2 * M
    wh = h - 2 * M
    dark = P["name"] == "dark"
    c.define(
        "drop",
        '<filter id="drop" x="-6%" y="-8%" width="112%" height="125%">'
        f'<feDropShadow dx="0" dy="5" stdDeviation="6" flood-color="{P["shadow"]}" '
        f'flood-opacity="{0.5 if dark else 0.12}"/></filter>',
    )
    c.add(
        f'<rect x="{x}" y="{y}" width="{w}" height="{wh}" rx="12" fill="{P["base"]}" filter="url(#drop)"/>',
        f'<path d="M{x},{y + BAR_H} V{y + 12} a12,12 0 0 1 12,-12 H{x + w - 12} a12,12 0 0 1 12,12 V{y + BAR_H} Z" '
        f'fill="{P["mantle"]}"/>',
        f'<path d="M{x},{y + BAR_H} H{x + w}" stroke="{P["crust"]}"/>',
        f'<rect x="{x + .5}" y="{y + .5}" width="{w - 1}" height="{wh - 1}" rx="11.5" fill="none" '
        f'stroke="{P["surface0"]}"/>',
    )
    for i, key in enumerate(("accent", "fg", "mute")):
        c.add(f'<circle cx="{x + 20 + i * 20}" cy="{y + BAR_H / 2}" r="6" fill="{P[key]}"/>')
    t = Term(c, P, 0, y + (BAR_H - 12.5 * 1.4) / 2, size=12.5, lh=1.4)
    t.x = x + (w - cells(title) * t.cw) / 2
    c.add(t.text(0, 0, title, "subtext0"))
    return x + PAD, y + BAR_H + 16


def prompt(cfg: dict) -> str:
    user = cfg["profile"]["user"]
    return f"[accent b]{user}[/][overlay1]@[/][fg b]dmu[/] [fg2 b]~[/] [overlay0]\u276f[/] "


def loop_move(c: Canvas, name: str, total: float, points: list[tuple[float, str]],
              timing: str = "ease-in-out", static: str = "none") -> str:
    """A looping transform animation given as (seconds, transform) points."""
    kf = "".join(f"{t / total * 100:.3f}%{{transform:{v}}}" for t, v in points)
    c.style(f"@keyframes {name}{{{kf}}}"
            f".{name}{{transform:{static};animation:{name} {total:.2f}s {timing} infinite}}")
    return name


def fireflies(c: Canvas, P: dict, n: int, x0: float, y0: float, x1: float, y1: float, seed: int = 11) -> str:
    """Small dots drifting slowly upwards behind the text."""
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        sx = rnd.uniform(x0, x1)
        sway = rnd.uniform(8, 26)
        dur = rnd.uniform(11, 20)
        delay = -rnd.uniform(0, dur)
        op = rnd.uniform(0.18, 0.5)
        r = rnd.uniform(1.2, 2.2)
        name = c.uid("ff")
        c.style(
            f"@keyframes {name}{{0%{{transform:translate(0,0);opacity:0}}"
            f"20%{{opacity:{op:.2f}}}70%{{opacity:{op * .7:.2f}}}"
            f"100%{{transform:translate({sway:.0f}px,{y0 - y1:.0f}px);opacity:0}}}}"
            f".{name}{{animation:{name} {dur:.1f}s ease-in-out {delay:.1f}s infinite}}"
        )
        color = P["accent2"] if rnd.random() < 0.6 else P["fg2"]
        out.append(f'<g class="{name}"><circle cx="{sx:.0f}" cy="{y1:.0f}" r="{r:.1f}" fill="{color}"/></g>')
    return "".join(out)


def cursor(c: Canvas, P: dict, t: Term, col: float, row: float, cls: str = "") -> str:
    c.style(".blink{animation:blink 1.05s step-end infinite}@keyframes blink{50%{opacity:0}}", key="blink")
    x = t.col_x(col)
    y = t.row_y(row) + (t.lh - t.size * 1.3) / 2
    k = f' class="{cls}"' if cls else ""
    return (f'<g{k}><rect class="blink" x="{x:.1f}" y="{y:.1f}" width="{t.cw:.1f}" '
            f'height="{t.size * 1.3:.1f}" rx="1.5" fill="{P["accent"]}" opacity=".85"/></g>')


# ------------------------------------------------------------------- header

def header(cfg: dict, P: dict) -> str:
    rows = art.banner(cfg["profile"]["banner"])
    bw = max(len(r) for r in rows)
    inner = W - 2 * M - 2 * PAD
    size = min(float(cfg["header"].get("max_size", 28)), inner / bw / 0.6)
    lh = 1.26
    line = 14 * 1.5
    cmds = cfg["header"]["commands"]
    n_out = max(len(c["output"]) for c in cmds)

    oy = M + BAR_H + 16
    y_banner = oy + line + 50
    banner_h = len(rows) * size * lh
    y_sub = y_banner + banner_h + 10
    y_term = y_sub + 21 + 18
    H = y_term + (1 + n_out) * line + 26 + M

    c = Canvas(W, H)
    ox, oy = window(c, P, H, cfg["header"]["title"])
    c.add(fireflies(c, P, 18, M + 10, M + BAR_H + 10, W - M - 20, H - M - 10))

    small = Term(c, P, ox, oy, size=14, lh=1.5)
    c.add(small.text(0, 0, cfg["header"]["last_login"].format(date=date.today().strftime("%a %b %d")), "overlay1"))

    # ---- banner: solid blocks in one path, one gradient, no seams
    bt = Term(c, P, 0, y_banner, size=size, lh=lh)
    bt.x = (W - bw * bt.cw) / 2
    stops = [P["accent2"], P["accent"], P["fg2"], P["fg"]]
    grad = c.uid("bg")
    c.define(grad, f'<linearGradient id="{grad}" gradientUnits="userSpaceOnUse" x1="{bt.x:.0f}" '
                   f'x2="{bt.x + bw * bt.cw:.0f}" y1="0" y2="0">' +
             "".join(f'<stop offset="{i / (len(stops) - 1):.2f}" stop-color="{s}"/>'
                     for i, s in enumerate(stops)) + "</linearGradient>")
    shade, runs = [], []
    for r, row in enumerate(rows):
        for col, ch in enumerate(row):
            if ch not in " \u2588":
                shade.append(bt.text(col, r, ch, mix(ramp(stops, col / max(1, bw - 1)), P["base"], 0.3)))
        runs += bt.blocks(0, r, row)
    d = "".join(f"M{x:.2f},{y:.2f}h{w:.2f}v{h2 + .05:.2f}h{-w:.2f}Z" for x, y, w, h2 in runs)
    bx0, by0 = bt.x, bt.row_y(0)

    # ---- she peeks out from behind the last letter of the top row
    top = rows[0]
    end = top.rfind("\u2588")
    begin = end
    while begin > 0 and top[begin - 1] == "\u2588":
        begin -= 1
    pxs = 1.7
    sw, sh = sprite.W * pxs, sprite.HEIGHT * pxs
    sx = bt.x + (begin + end + 1) / 2 * bt.cw - sw / 2
    sy = by0 + 2 - 43 * pxs   # her face clears the letters, her chest hides behind them
    hop = loop_move(c, "hop", 7.0, [(0, "translateY(0)"), (5.0, "translateY(0)"), (5.1, "translateY(-7px)"),
                                    (5.3, "translateY(0)"), (5.5, "translateY(-3px)"), (5.7, "translateY(0)"),
                                    (7.0, "translateY(0)")])
    cls = frames(c, "bl", [(0, 3.2), (1, .13), (0, .2), (1, .13), (0, 2.54)], 2)
    c.add(f'<g class="{hop}">')
    sprite.render(c, P, sx, sy, pxs)
    c.add(f'<g class="{cls[1]}">')
    sprite.render_lid(c, P, sx, sy, pxs)
    c.add("</g></g>")

    # letters go on top of her, so she looks like she is hiding behind them
    c.add("".join(shade), f'<path d="{d}" fill="url(#{grad})"/>')

    # a light band sweeping across the letters every few seconds
    clip = c.uid("bc")
    c.define(clip, f'<clipPath id="{clip}"><path d="{d}"/></clipPath>')
    shine = c.uid("sh")
    c.define(shine, f'<linearGradient id="{shine}" x1="0" x2="1">'
                    '<stop offset="0" stop-color="#fff" stop-opacity="0"/>'
                    f'<stop offset=".5" stop-color="#fff" stop-opacity="{0.5 if P["name"] == "dark" else 0.65}"/>'
                    '</linearGradient>')
    c.style(f"@keyframes sweep{{0%{{transform:translateX({bx0 - 170:.0f}px)}}"
            f"26%,100%{{transform:translateX({bx0 + bw * bt.cw + 60:.0f}px)}}}}"
            f".sweep{{animation:sweep 8s ease-in-out 1.4s infinite;transform:translateX(-500px)}}")
    c.add(f'<g clip-path="url(#{clip})"><rect class="sweep" x="0" y="{by0:.0f}" width="130" '
          f'height="{banner_h:.0f}" fill="url(#{shine})"/></g>')

    # ---- subtitle under the banner
    st = Term(c, P, 0, y_sub, size=14, lh=1.5)
    m = cfg["header"]["subtitle"]
    st.x = (W - cells(plain(m)) * st.cw) / 2
    c.add(st.markup(0, 0, m)[0])

    # ---- typing terminal
    tt = Term(c, P, ox, y_term, size=14, lh=1.5)
    pm = prompt(cfg)
    pcols = cells(plain(pm))
    c.add(tt.markup(0, 0, pm)[0])

    per_char, gap_out, hold, gap_next = 0.052, 0.32, 2.6, 0.42
    seq, t = [], 0.35
    for item in cmds:
        seq.append((t, item))
        t += len(item["cmd"]) * per_char + gap_out + hold + gap_next
    total = t
    clock = Clock(c, total, "ty")
    moves: list[tuple[float, float]] = []
    for k, (t0, item) in enumerate(seq):
        cmd = item["cmd"]
        t_typed = t0 + len(cmd) * per_char
        t_out = t_typed + gap_out
        t_clear = t_out + hold
        c.add(tt.text(pcols, 0, cmd, "text", cls=lambda i, a=t0, b=t_clear, first=(k == 0):
                      clock.show(a + (i + 1) * per_char, b, static=first)))
        for j, out in enumerate(item["output"]):
            oc = clock.show(t_out + j * 0.1, t_clear, static=(k == 0))
            c.add(f'<g class="{oc}">{tt.markup(0, 1 + j, out)[0]}</g>')
        col = pcols
        moves.append((t0, col))
        for i, ch in enumerate(cmd):
            col += 1 if ch == " " else pick(ch)[3]
            moves.append((t0 + (i + 1) * per_char, col))
        moves.append((t_clear, pcols))
    kf = "".join(f"{tm / total * 100:.3f}%{{transform:translateX({(cl - pcols) * tt.cw:.1f}px)}}" for tm, cl in moves)
    c.style(f"@keyframes curmove{{0%{{transform:translateX(0)}}{kf}}}"
            f".curmove{{animation:curmove {total:.2f}s step-end infinite;"
            f"transform:translateX({cells(cmds[0]['cmd']) * tt.cw:.1f}px)}}")
    c.add(cursor(c, P, tt, pcols, 0, "curmove"))
    return c.svg(cfg["header"]["alt"])


# ----------------------------------------------------------------- neofetch

def cat_card(c: Canvas, P: dict, bx: float, by: float, bw: float, bh: float, px: float = 2.75) -> None:
    """Miku in a small box: a portrait disc, a breath, a blink, and a nya~."""
    T = 8.0
    c.add(f'<rect x="{bx:g}" y="{by:g}" width="{bw:g}" height="{bh:g}" rx="16" fill="{P["mantle"]}" '
          f'stroke="{P["surface0"]}"/>')
    sw, sh = sprite.W * px, sprite.HEIGHT * px
    sx = bx + (bw - sw) / 2
    sy = by + (bh - sh) / 2 - 2

    # a disc behind her, so the white shirt has something to sit on
    # a soft violet wash, so the white shirt has something to sit against
    gid = c.uid("cv")
    c.define(gid, f'<linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">'
                  f'<stop offset="0" stop-color="{P["accent2"]}" stop-opacity=".08"/>'
                  f'<stop offset=".62" stop-color="{P["accent2"]}" stop-opacity=".20"/>'
                  f'<stop offset="1" stop-color="{P["accent"]}" stop-opacity=".30"/>'
                  f'</linearGradient>')
    c.add(f'<rect x="{bx:g}" y="{by:g}" width="{bw:g}" height="{bh:g}" rx="16" fill="url(#{gid})"/>')

    c.style("@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-3px)}}"
            ".bob{animation:bob 4.6s ease-in-out infinite}", key="bob")

    cls = frames(c, "ck", [(0, 3.6), (1, .12), (0, .2), (1, .12), (0, 3.96)], 2)
    c.add('<g class="bob">')
    sprite.render(c, P, sx, sy, px)
    c.add(f'<g class="{cls[1]}">')
    sprite.render_lid(c, P, sx, sy, px)
    c.add("</g></g>")

    # a heart drifts up, then nya~ pops out in the corner
    clock = Clock(c, T, "cn")
    heart = glyph(c, "\u2661", bx + bw - 34, by + 38, 13, True, (), "fill=\"" + P["accent"] + "\"")
    drift = loop_move(c, "clove", T, [(0, "translateY(10px)"), (4.6, "translateY(10px)"),
                                      (6.4, "translateY(-12px)"), (T, "translateY(-12px)")], "linear")
    c.add(f'<g class="{clock.show(4.6, 6.6)}"><g class="{drift}">{heart}</g></g>')

    word, ms = "nya~", 13.0
    mx = bx + bw - 12 - len(word) * ms * 0.6
    for i, ch in enumerate(word):
        t0 = 5.0 + i * 0.09
        nm = loop_move(c, f"ny{i}", T, [(0, "translateY(0)"), (t0, "translateY(0)"),
                                        (t0 + .1, "translateY(-4px)"), (t0 + .26, "translateY(0)"), (T, "translateY(0)")])
        c.add(f'<g class="{clock.show(4.9, 6.6)}"><g class="{nm}">'
              f'{glyph(c, ch, mx + i * ms * 0.6, by + bh - 22, ms, True, (), "fill=\"" + P["accent2"] + "\"")}'
              f'</g></g>')


INFO_COL = 40


def _uptime(days: int) -> str:
    years, rest = divmod(days, 365)
    bits = []
    if years:
        bits.append(f"{years} year{'s' if years > 1 else ''}")
    bits.append(f"{rest} day{'s' if rest != 1 else ''}")
    return ", ".join(bits)


def neofetch(cfg: dict, P: dict, s: dict) -> str:
    info = info_lines(cfg, s)
    size, lh = 14, 1.5
    line = size * lh
    rows = 2 + len(info) + 1
    H = M * 2 + BAR_H + 16 + rows * line + 12
    c = Canvas(W, H)
    ox, oy = window(c, P, H, "neofetch")
    t = Term(c, P, ox, oy, size=size, lh=lh)
    c.add(t.markup(0, 0, prompt(cfg) + "neofetch")[0])

    bw, bh = 246, 212
    mid = (t.row_y(2) + t.row_y(2 + len(info))) / 2
    cat_card(c, P, ox, mid - bh / 2, bw, bh)

    for r, item in enumerate(info):
        if isinstance(item, str):
            c.add(t.markup(INFO_COL, 2 + r, item)[0])
        else:
            c.add(item(t, INFO_COL, 2 + r))
    return c.svg("neofetch: Pond, and the numbers GitHub keeps")


def info_lines(cfg: dict, s: dict) -> list:
    login = cfg["profile"]["user"]
    key = lambda n: f"[mute b]{n:<10}[/]"  # noqa: E731
    num = lambda v: f"[fg b]{v:,}[/]"  # noqa: E731
    dot = " [overlay0]\u00b7[/] "
    lines: list = [
        f"[accent b]{login}[/][overlay1]@[/][mute b]github[/]",
        "[overlay0]" + "\u2500" * 13 + "[/]",
    ]
    for name, value in cfg["neofetch"]["about"]:
        lines.append(key(name) + value)
    lines += [
        key("uptime") + _uptime(s["days"]),
        key("repos") + num(s["repos"]) + " public" + dot + f"[fg2 b]\u2605[/] {num(s['stars'])}",
        key("commits") + num(s["commits"]) + " in the last year",
        key("prs") + num(s["prs"]) + dot + "issues " + num(s["issues"]),
        key("followers") + num(s["followers"]) + dot + "following " + num(s["following"]),
        key("streak") + num(s["current"]) + f" day{'s' if s['current'] != 1 else ''}"
        + f" [overlay1](best {s['best']})[/]",
    ]

    total = sum(v for _, v in s["languages"]) or 1
    langs = [(n, v) for n, v in s["languages"] if v / total >= 0.02][:3]

    def bar(t: Term, col: float, row: float, langs=langs):
        n = 30
        widths = [max(1, round(v / sum(x for _, x in langs) * n)) for _, v in langs]
        widths[0] += n - sum(widths)
        out = [t.markup(col, row, key("languages"))[0]]
        x = 1
        for (_, _), wdt, accent in zip(langs, widths, ["accent", "fg2", "mute", "fg3"]):
            out.append(t.text(col + 10 + x, row, "\u2588" * wdt, accent))
            x += wdt
        return "".join(out)

    def legend(t: Term, col: float, row: float, langs=langs):
        tot = sum(v for _, v in langs)
        m = " ".join(f"[{a}]\u25cf[/] {name} [overlay1]{v / tot * 100:.0f}%[/]"
                     for (name, v), a in zip(langs[:4], ["accent", "fg2", "mute", "fg3"]))
        return t.markup(col + 11, row, m)[0]

    if langs:
        lines += [bar, legend]
    else:
        lines.append(key("languages") + "[overlay1]no public code yet[/]")

    def palette(t: Term, col: float, row: float):
        out = []
        for i, accent in enumerate(["accent", "accent2", "fg2", "mute", "fg3", "overlay0", "fg", "surface2"]):
            out.append(t.text(col + i * 4, row, "\u2588\u2588\u2588", accent))
        return "".join(out)

    lines.append(palette)
    return lines


# ----------------------------------------------------------------- heat grid

MONTHS = ["1\u6708", "2\u6708", "3\u6708", "4\u6708", "5\u6708", "6\u6708",
          "7\u6708", "8\u6708", "9\u6708", "10\u6708", "11\u6708", "12\u6708"]


def day_cell(P: dict, x: float, y: float, size: float, level: int) -> str:
    if level == 0:  # a quiet day is just a dot
        return f'<circle cx="{x + size / 2:g}" cy="{y + size / 2:g}" r="1.6" fill="{P["surface2"]}"/>'
    return (f'<rect x="{x:g}" y="{y:g}" width="{size:g}" height="{size:g}" rx="2" '
            f'fill="{P["heat"][level]}"/>')


def activity(cfg: dict, P: dict, s: dict) -> str:
    weeks = s["weeks"][-53:]
    nweeks = len(weeks)
    pitch, cell, label_w = 14, 12, 26
    line = 14 * 1.5
    y_grid = M + BAR_H + 16 + 2 * line
    y_cells = y_grid + 20
    y_sum = y_cells + 7 * pitch + 16
    H = y_sum + line + 18 + M
    c = Canvas(W, H)
    ox, oy = window(c, P, H, "~/activity")
    t = Term(c, P, ox, oy, size=14, lh=1.5)
    c.add(t.markup(0, 0, prompt(cfg) + "git log --graph --all")[0])

    grid_x = round(ox + label_w)
    mt = Term(c, P, grid_x, y_grid, size=11.5, lh=1.4)
    last = date.fromisoformat(weeks[0][0][0]).month
    for wi, week in enumerate(weeks):
        d0 = date.fromisoformat(week[0][0])
        if d0.month != last and wi < nweeks - 2:
            c.add(mt.text(wi * pitch / mt.cw, 0, MONTHS[d0.month - 1], "subtext0"))
        last = d0.month

    dt = Term(c, P, ox, y_cells, size=11.5, lh=pitch / 11.5)
    for r, lab in ((1, "\u4e00"), (3, "\u4e09"), (5, "\u4e94")):
        c.add(dt.text(0, r, lab, "overlay1"))

    # a soft glow travels across the grid, one column at a time
    c.style("@keyframes glow{0%{opacity:0}6%{opacity:.16}14%{opacity:0}100%{opacity:0}}", key="glow")
    step = 0.12
    for wi, week in enumerate(weeks):
        x = grid_x + wi * pitch
        body = []
        for iso, level, _ in week:
            wd = (date.fromisoformat(iso).weekday() + 1) % 7
            body.append(day_cell(P, x, round(y_cells + wd * pitch), cell, level))
        c.add(f'<g>{"".join(body)}'
              f'<rect x="{x - 1}" y="{y_cells - 1}" width="{pitch}" height="{7 * pitch}" rx="2" '
              f'fill="{P["accent2"]}" style="animation:glow {nweeks * step:.2f}s linear infinite;'
              f'animation-delay:-{wi * step:.2f}s"/></g>')

    bt = Term(c, P, ox, y_sum, size=14, lh=1.5)
    streak = s["current"]
    c.add(bt.markup(0, 0, f"[accent b]{s['contributions']:,}[/] contributions in the last year [overlay0]\u00b7[/] "
                          f"streak [fg b]{streak}[/] day{'s' if streak != 1 else ''}")[0])

    # legend, right-aligned
    right = W - M - PAD
    lx = right - (5 * 16 + 2 * 10)
    cy = bt.row_y(0) + (bt.lh - cell) / 2
    out = [Term(c, P, lx, y_sum, size=14, lh=1.5).text(0, 0, "\u5c11", "overlay1")]
    x = lx + 2 * bt.cw + 4
    for level in range(5):
        out.append(day_cell(P, round(x), round(cy), cell, level))
        x += 16
    out.append(Term(c, P, x + 2, y_sum, size=14, lh=1.5).text(0, 0, "\u591a", "overlay1"))
    c.add("".join(out))
    return c.svg("One year of contributions on a character grid")


# --------------------------------------------------------------------- stack

def stack(cfg: dict, P: dict) -> str:
    files = cfg["stack"]["files"]
    line = 14 * 1.5
    H = M * 2 + BAR_H + 16 + 2 * line + 14
    c = Canvas(W, H)
    ox, oy = window(c, P, H, "~/stack")
    t = Term(c, P, ox, oy, size=14, lh=1.5)
    c.add(t.markup(0, 0, prompt(cfg) + "ls ~/stack")[0])
    col = 0
    for name, accent in files:
        c.add(t.text(col, 1, name, accent, bold=True))
        col += cells(name) + 3
    return c.svg("Stack: " + ", ".join(n for n, _ in files))


# -------------------------------------------------------------------- footer

def footer(cfg: dict, P: dict) -> str:
    line = 14 * 1.45
    H = M * 2 + BAR_H + 16 + line * 9 + 14
    c = Canvas(W, H)
    ox, oy = window(c, P, H, cfg["footer"]["title"])
    t = Term(c, P, ox, oy, size=14, lh=1.45)
    c.add(t.markup(0, 0, prompt(cfg) + "exit")[0])

    pxf = 1.3
    sfw = sprite.W * pxf
    fx = ox + 4
    fy = oy + line * 2.4
    sprite.render(c, P, fx, fy, pxf)
    sprite.render_lid(c, P, fx, fy, pxf)

    cls = frames(c, "zz", [(i, 0.75) for i in range(len(art.SLEEP_Z))], len(art.SLEEP_Z))
    zt = Term(c, P, fx + sfw + 4, fy + 2, size=13, lh=1.4)
    for k, frame in enumerate(art.SLEEP_Z):
        c.style(f".{cls[k]}{{opacity:{1 if k == 2 else 0}}}")
        z = "".join(zt.text(col, row, ch, ["accent", "fg2", "mute"][i % 3], bold=True)
                    for i, (row, col, ch) in enumerate(frame))
        c.add(f'<g class="{cls[k]}">{z}</g>')

    tx = fx + sfw + 34
    txt = Term(c, P, tx, fy + 2, size=14, lh=1.5)
    for r, m in enumerate(cfg["footer"]["lines"]):
        c.add(txt.markup(0, r * 1.35, m.format(date=date.today().isoformat()))[0])
    c.add(t.markup(0, 8, "[overlay1]exit 0[/] [overlay0]# 该回去了[/]")[0])
    return c.svg(cfg["footer"]["alt"])


# -------------------------------------------------------------------- badges

def badge(label: str, value: str, accent: str, P: dict) -> str:
    size, h = 13, 28
    lw = cells(label) * size * 0.6 + 22
    vw = cells(value) * size * 0.6 + 22
    c = Canvas(round(lw + vw), h)
    c.add(
        f'<rect width="{lw + vw:.0f}" height="{h}" rx="7" fill="{P["surface0"]}"/>',
        f'<path d="M7,0 H{lw:.0f} V{h} H7 a7,7 0 0 1 -7,-7 V7 a7,7 0 0 1 7,-7 Z" fill="{P[accent]}"/>',
    )
    t1 = Term(c, P, 11, (h - size * 1.4) / 2, size=size, lh=1.4)
    c.add(t1.text(0, 0, label, "crust" if P["name"] == "dark" else "base", bold=True))
    t2 = Term(c, P, lw + 11, (h - size * 1.4) / 2, size=size, lh=1.4)
    c.add(t2.text(0, 0, value, "text", bold=True))
    return c.svg(f"{label}: {value}")
