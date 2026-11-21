#!/usr/bin/env python3
"""Build the 20 November 2026 world-news front page, v2, 1024x1024.

Same front page as v1 (36 stories, same facts, same lead, same layout),
rebuilt to fix two bugs the user found in v1:
1. Overlapping text in the card rows. In v1 the card 5 kicker
   ("5 · STRAIT OF HORMUZ · MIDDLE EAST") measured 216 px in a 196 px
   column and bled into card 6, and card titles sat 4 px from the edge.
   Fix: shorter kickers, a smaller card title font, and every card's text
   drawn on its own offscreen canvas exactly the card's width, so no
   glyph can ever cross into the next card. Lines that would still exceed
   the width are cut with an ellipsis.
2. Soft art. All 13 pictures were generated fresh at full resolution,
   downscaled with Lanczos, and the page is saved at JPEG quality 90.

Deterministic: same input art, same output bytes. No em dash anywhere.
"""
import glob
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
WORK = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(WORK, "assets")

PAPER = (250, 244, 231)
INK = (26, 22, 18)
RED = (178, 34, 28)
GREY = (110, 104, 92)
MAPFILL = (64, 64, 64)
RULE = (26, 22, 18)
CARD_RULE = (200, 192, 176)

REGION_COLORS = {
    "Europe": (58, 90, 140),
    "Americas": (120, 70, 130),
    "Asia": (200, 90, 40),
    "Middle East": (30, 120, 90),
    "Global": (120, 110, 100),
    "Africa": (190, 150, 30),
    "Oceania": (40, 140, 160),
}

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


F_MAST = font("DejaVuSans-Bold.ttf", 25)
F_DATE = font("DejaVuSerif-Bold.ttf", 42)
F_ANCHOR = font("DejaVuSans-Bold.ttf", 16)
F_NUM = font("DejaVuSans-Bold.ttf", 22)
F_LAB = font("DejaVuSans.ttf", 10)
F_REG = font("DejaVuSans-Bold.ttf", 10)
F_KICK = font("DejaVuSans-Bold.ttf", 11)
F_H1 = font("DejaVuSerif-Bold.ttf", 27)
F_DEK = font("DejaVuSans.ttf", 13)
F_H2 = font("DejaVuSans-Bold.ttf", 19)
F_BODY2 = font("DejaVuSans.ttf", 12)
F_SRC = font("DejaVuSans.ttf", 10)
F_CARD_KICK = font("DejaVuSans-Bold.ttf", 9)
F_CARD_TITLE = font("DejaVuSans-Bold.ttf", 13)
F_CARD_BODY = font("DejaVuSans.ttf", 10)
F_CARD_SRC = font("DejaVuSans.ttf", 9)
F_MAPHEAD = font("DejaVuSans-Bold.ttf", 12)
F_BRIEF = font("DejaVuSans.ttf", 9)
F_BRIEF_N = font("DejaVuSans-Bold.ttf", 9)
F_BRIEF_S = font("DejaVuSans.ttf", 9)
F_DATECHECK_T = font("DejaVuSans-Bold.ttf", 12)
F_DATECHECK = font("DejaVuSans.ttf", 11)
F_FOOT = font("DejaVuSans.ttf", 10)


def art(prefix):
    hits = sorted(glob.glob(os.path.join(ASSETS, "media-generation-" + prefix + "-*.webp")))
    if not hits:
        raise SystemExit("missing art: " + prefix)
    return Image.open(hits[0]).convert("RGB")


def cover(im, w, h):
    """Centre crop to w x h, keeping the middle band. Lanczos downscale."""
    iw, ih = im.size
    s = max(w / iw, h / ih)
    im2 = im.resize((int(iw * s) + 1, int(ih * s) + 1), Image.LANCZOS)
    x = (im2.size[0] - w) // 2
    y = (im2.size[1] - h) // 2
    return im2.crop((x, y, x + w, y + h))


def wrap(d, text, f, width):
    lines = []
    for para in text.split("\n"):
        line = ""
        for word in para.split(" "):
            trial = (line + " " + word).strip()
            if d.textlength(trial, font=f) <= width or not line:
                line = trial
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)
    return lines


def fit_line(d, text, f, width):
    """Cut a single line with an ellipsis if it would exceed width."""
    if d.textlength(text, font=f) <= width:
        return text
    while text and d.textlength(text + "…", font=f) > width:
        text = text[:-1]
    return text + "…"


def draw_tag(d, x_right, y, text):
    d.text((x_right - d.textlength(text, font=F_CARD_SRC), y), text,
           font=F_CARD_SRC, fill=RED)


# (num, place, region, title, body, source, tag, art prefix)
# Kicker place names are kept short on purpose: the v1 kicker for card 5
# measured 216 px in a 196 px column and bled into card 6.
CARDS = [
    (4, "ANTALYA", "GLOBAL", "Climate talks run past their deadline",
     "No deal on the final day. The draft has no mention of fossil fuels.",
     "Le Monde · UN News", "REPORTED", "card-cop31"),
    (5, "HORMUZ", "MIDDLE EAST", "A tanker burns in the oil chokepoint",
     "A projectile hit a tanker off Oman. Iran blamed a mine, unverified.",
     "Reuters · UKMTO", "REPORTED", "card-hormuz"),
    (6, "BRUSSELS", "EUROPE", "Britain and the EU rebuild a piece of Brexit",
     "Food trade worth 5.1bn a year, carbon markets linked, 100,000 visas.",
     "Reuters · AP", "REPORTED", "card-euuk"),
    (7, "NARVA", "EUROPE", "Estonia seals its border with Russia",
     "Five crossings close 1 December after a GRU-linked arson attempt.",
     "Reuters", "REPORTED", "card-estonia"),
    (8, "JURF AL-SAKHAR", "MIDDLE EAST", "Baghdad walks back into a militia town",
     "Iraqi forces entered the militia stronghold after 12 years.",
     "AFP", "REPORTED", "card-iraq"),
    (9, "GAZA", "MIDDLE EAST", "Six more killed as the truce keeps failing",
     "Six killed on Friday. Over 1,600 dead since the ceasefire began.",
     "AFP", "REPORTED", "card-gaza"),
    (10, "DHAKA", "ASIA", "A minister's home is firebombed",
     "A second day of violence. Police arrested 124 in Dhaka in 24 hours.",
     "Daily Jagran", "REPORTED", "card-bangladesh"),
    (11, "ST. LOUIS", "AMERICAS", "Bayer's $7.25bn Roundup deal approved",
     "A Missouri judge approved the deal, ending a decade of cancer claims.",
     "Reuters · AP", "REPORTED", "card-bayer"),
    (12, "JUNIN", "AMERICAS", "A 6.7 quake shakes the Andes",
     "Felt in Lima. No casualties and no damage reported. No tsunami threat.",
     "AP · USGS", "REPORTED", "card-peru"),
    (13, "MOSCOW", "EUROPE", "Europe weighs Putin's Moscow invitation",
     "France would go with a full role; Russia is preparing to host the E3.",
     "EuropeSays", "CLAIM", "card-moscow"),
]

# (num, text, source) - one line each, kept short on purpose
BRIEFS = [
    (14, "GTA VI made $3.79bn in a day, Rockstar said.", "Game Informer"),
    (15, "Trump pardoned Pete Rose, baseball's hit king.", "ESPN"),
    (16, "Alcaraz beat Cobolli 6-4, 6-1 in Turin.", "ATP"),
    (17, "Medvedev beat Tiafoe 6-3, 6-4.", "ATP"),
    (18, "Record X-ray laser hit 0.04 nanometres.", "phys.org"),
    (19, "Bending Spoons revenue rose 125% to $780m.", "Panabee"),
    (20, "Espanyol beat Athletic Club 1-0.", "Sofascore"),
    (21, "Cologne held Bayern Munich 1-1.", "Sofascore"),
    (22, "Pakistan beat Sri Lanka by 8 wickets.", "ESPNcricinfo"),
    (23, "Lakshya Sen won a 13th straight match.", "IANS"),
    (24, "Taiwan's Taiex fell 6.2% on Friday.", "Int. Intrigue"),
    (25, "WeRide revenue rose 88% to RMB321.5m.", "FinScans"),
    (26, "RLX revenue rose 70% to RMB1.92bn.", "Panabee"),
    (27, "Rankireddy and Shetty reached the doubles semis.", "IANS"),
    (28, "India A beat Nepal in Doha.", "Apex"),
    (29, "Crystal shells guide materials growth, Cornell said.", "Cornell"),
    (30, "Palo Alto rose 6.4% after an earnings beat.", "Zacks"),
    (31, "Nvidia fell 14% on an SEC accounting probe.", "Motley Fool"),
    (32, "Broadcom fell 10% after Google cut TPU orders.", "Ainvest"),
    (33, "BJ's earnings per share rose 50.4% to $1.73.", "Zacks"),
    (34, "Al-Ahli beat Al-Nassr 3-1 in Jeddah.", "Sofascore"),
    (35, "US group won Kenya's $60bn rare-earth project.", "Int. Intrigue"),
    (36, "Nicholls made 175 not out for New Zealand.", "Cricbuzz"),
]

REGIONS = [("EUROPE", 10), ("AMERICAS", 10), ("ASIA", 9), ("MIDDLE EAST", 4),
           ("GLOBAL", 1), ("AFRICA", 1), ("OCEANIA", 1)]

NUMBERS = [
    ("3", "Dnipro bridges hit"),
    ("8", "killed across Ukraine"),
    ("300,000+", "evacuated for Akvan"),
    ("-3.7%", "S&P 500 on Friday"),
    ("$7.25bn", "Bayer Roundup deal"),
    ("100,000", "youth visas, EU-UK"),
]

# (num, lon, lat, dx, dy) - dx/dy nudge pins apart in the Europe cluster
PINS = [
    (1, 30.5, 50.5, 2, 6), (2, 21.0, 52.0, -6, -10), (3, 86.0, 20.0, 0, 0),
    (4, 30.7, 36.9, 0, 0), (5, 57.0, 25.5, 0, 0), (6, 4.4, 50.8, -6, 4),
    (7, 28.2, 59.4, 4, -8), (8, 44.2, 32.8, 0, 8), (9, 34.5, 31.4, 6, 0),
    (10, 90.4, 23.8, 0, 0), (11, -96.0, 38.5, 0, 0), (12, -75.0, -11.0, 0, 0),
    (13, 37.6, 55.8, 8, -4),
]

# Hand drawn continent outlines, lon/lat points
CONTINENTS = [
    [(-168, 66), (-158, 71), (-140, 70), (-125, 71), (-110, 68), (-95, 69),
     (-85, 66), (-75, 62), (-65, 60), (-55, 52), (-60, 47), (-70, 44),
     (-75, 39), (-80, 32), (-81, 26), (-90, 21), (-97, 16), (-105, 20),
     (-110, 23), (-117, 33), (-125, 40), (-125, 49), (-130, 55), (-145, 60),
     (-155, 58), (-165, 60), (-168, 66)],
    [(-79, 9), (-77, 4), (-80, -3), (-81, -6), (-77, -12), (-72, -18),
     (-70, -23), (-68, -33), (-65, -41), (-62, -45), (-68, -50), (-70, -54),
     (-66, -55), (-70, -50), (-73, -44), (-73, -37), (-70, -30), (-70, -20),
     (-75, -15), (-79, -8), (-81, -4), (-79, 3), (-79, 9)],
    [(-17, 15), (-17, 21), (-16, 27), (-10, 31), (-6, 35), (0, 36), (10, 37),
     (20, 32), (30, 31), (32, 31), (35, 28), (43, 12), (51, 12), (58, 20),
     (57, 25), (52, 26), (48, 29), (44, 29), (40, 15), (39, 6), (41, -2),
     (40, -10), (36, -18), (33, -26), (28, -33), (20, -35), (17, -32),
     (15, -27), (13, -18), (12, -10), (9, -1), (9, 4), (6, 4), (-8, 5),
     (-13, 8), (-17, 15)],
    [(-10, 37), (-9, 43), (-2, 44), (-2, 48), (0, 50), (2, 51), (5, 53),
     (8, 57), (10, 59), (18, 56), (21, 55), (24, 58), (28, 59), (30, 60),
     (30, 62), (25, 65), (20, 70), (30, 71), (40, 68), (50, 69), (60, 69),
     (68, 66), (60, 60), (55, 55), (50, 50), (45, 47), (40, 44), (36, 36),
     (30, 36), (26, 38), (23, 36), (19, 40), (15, 38), (12, 42), (8, 44),
     (3, 43), (0, 40), (-2, 37), (-6, 36), (-9, 37), (-10, 37)],
    [(65, 25), (68, 23), (72, 20), (77, 15), (80, 13), (80, 10), (77, 8),
     (80, 7), (85, 19), (88, 22), (91, 22), (94, 17), (98, 10), (100, 6),
     (103, 2), (104, 1), (100, 2), (98, 8), (97, 14), (94, 17), (92, 21),
     (89, 22), (85, 19), (82, 16), (80, 13), (77, 8), (75, 12), (73, 16),
     (70, 21), (67, 25), (65, 25)],
    [(95, -15), (105, -12), (115, -14), (122, -17), (130, -12), (137, -12),
     (142, -11), (147, -19), (150, -22), (153, -27), (150, -37), (145, -38),
     (140, -38), (135, -35), (130, -32), (124, -33), (118, -35), (114, -32),
     (113, -25), (114, -22), (110, -20), (104, -18), (100, -15), (95, -15)],
]

# Card text zone geometry. The text canvas is exactly one card wide, so a
# long kicker or headline is cut at the card edge instead of crossing over.
CW = 196
CARD_TEXT_H = 88


def render_card_text(card):
    """Draw one card's kicker, title, body, source and tag on a canvas
    exactly CW wide. Returns the canvas plus the widest line drawn, for
    the build-time check."""
    num, place, region, title, body, src, tag, _prefix = card
    canvas = Image.new("RGBA", (CW, CARD_TEXT_H), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas)
    kicker = fit_line(d, str(num) + " · " + place + " · " + region,
                      F_CARD_KICK, CW)
    d.text((0, 0), kicker, font=F_CARD_KICK, fill=RED)
    widest = d.textlength(kicker, font=F_CARD_KICK)
    tlines = wrap(d, title, F_CARD_TITLE, CW)
    ty = 14
    for ln in tlines[:2]:
        ln = fit_line(d, ln, F_CARD_TITLE, CW)
        d.text((0, ty), ln, font=F_CARD_TITLE, fill=INK)
        widest = max(widest, d.textlength(ln, font=F_CARD_TITLE))
        ty += 14
    blines = wrap(d, body, F_CARD_BODY, CW)
    by = 46
    for ln in blines[:2]:
        ln = fit_line(d, ln, F_CARD_BODY, CW)
        d.text((0, by), ln, font=F_CARD_BODY, fill=INK)
        widest = max(widest, d.textlength(ln, font=F_CARD_BODY))
        by += 11
    tag_text = "[" + tag + "]"
    tag_w = d.textlength(tag_text, font=F_CARD_SRC)
    src_text = fit_line(d, src, F_CARD_SRC, CW - tag_w - 6)
    d.text((0, 74), src_text, font=F_CARD_SRC, fill=INK)
    d.text((CW - tag_w, 74), tag_text, font=F_CARD_SRC, fill=RED)
    return canvas, widest


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # Masthead
    d.text((12, 6), "THE WORLD IN ONE DAY", font=F_MAST, fill=INK)
    right = "36 STORIES · 7 REGIONS"
    d.text((1000 - d.textlength(right, font=F_REG), 12), right, font=F_REG, fill=RED)
    d.line([(12, 34), (1000, 34)], fill=RULE, width=2)

    # Giant serif date
    d.text((12, 38), "Friday 20 November 2026", font=F_DATE, fill=INK)
    # Anchor line under the date
    d.text((12, 82), "The war reached NATO: Kyiv's bridges hit, missiles land in Poland",
           font=F_ANCHOR, fill=INK)

    # Numbers strip
    d.line([(12, 102), (1000, 102)], fill=RULE, width=1)
    bw = 1000 - 12
    seg = bw / 6.0
    for i, (num, lab) in enumerate(NUMBERS):
        x = 12 + i * seg
        if i:
            d.line([(x, 106), (x, 138)], fill=CARD_RULE, width=1)
        d.text((x + 6, 106), num, font=F_NUM, fill=RED)
        d.text((x + 6, 130), lab, font=F_LAB, fill=INK)
    d.line([(12, 144), (1000, 144)], fill=RULE, width=1)

    # Region bar, each segment at least 60 wide so its label fits
    total = sum(n for _, n in REGIONS)
    widths = []
    rest = 1000 - 12 - 60 * len(REGIONS)
    for name, n in REGIONS:
        widths.append(60 + int(round(rest * n / total)))
    widths[-1] += (1000 - 12) - sum(widths)
    x = 12
    for (name, n), w in zip(REGIONS, widths):
        d.rectangle([x, 150, x + w - 1, 164], fill=REGION_COLORS[name.title()])
        d.text((x + 2, 166), name + " " + str(n), font=F_REG, fill=INK)
        x += w

    # Hero 1: the lead. Kyiv bridges + Poland missiles, one story.
    hy = 180
    hh = 156
    im1 = cover(art("hero-kyiv"), 546, hh)
    img.paste(im1, (12, hy))
    tx = 570
    d.text((tx, hy + 2), "1 · KYIV AND POLAND · EUROPE", font=F_KICK, fill=RED)
    hlines = wrap(d, "The war reached NATO", F_H1, 430)
    yy = hy + 16
    for ln in hlines:
        d.text((tx, yy), ln, font=F_H1, fill=INK)
        yy += 30
    dek = ("Russia's biggest barrage of the month hit three Dnipro bridges in "
           "Kyiv. Two missiles and a drone came down in Poland. Eight killed. "
           "NATO called it a grave violation.")
    dlines = wrap(d, dek, F_DEK, 430)
    yy = hy + 80
    for ln in dlines:
        d.text((tx, yy), ln, font=F_DEK, fill=INK)
        yy += 16
    d.text((tx, hy + 140), "Reuters · AP · ISW", font=F_SRC, fill=INK)
    draw_tag(d, 1000, hy + 140, "[REPORTED]")

    # Heroes 2 and 3, image left, text right
    hy2 = 344
    hh2 = 118
    heroes2 = [
        ("hero-wallstreet", "2 · NEW YORK · AMERICAS", "The AI boom turned to bust",
         "The S&P 500 fell 3.7% and the Dow 949 points, both into correction. "
         "The Nasdaq lost 5.3%. Nvidia fell 13.8%.",
         "Reuters · WSJ", "REPORTED", 12),
        ("hero-akvan", "3 · ODISHA · ASIA", "The storm came. The shelters held.",
         "Cyclone Akvan made landfall near Gopalpur. More than 300,000 people "
         "had been moved to safety. No deaths reported.",
         "IMD · The Hindu", "REPORTED", 516),
    ]
    for prefix, kick, title, body, src, tag, x0 in heroes2:
        im2 = cover(art(prefix), 168, hh2)
        img.paste(im2, (x0, hy2))
        tx2 = x0 + 180
        d.text((tx2, hy2 + 2), kick, font=F_KICK, fill=RED)
        tlines = wrap(d, title, F_H2, 300)
        yy = hy2 + 16
        for ln in tlines:
            d.text((tx2, yy), ln, font=F_H2, fill=INK)
            yy += 20
        blines = wrap(d, body, F_BODY2, 300)
        yy = hy2 + 58
        for ln in blines:
            d.text((tx2, yy), ln, font=F_BODY2, fill=INK)
            yy += 14
        d.text((tx2, hy2 + 104), src, font=F_SRC, fill=INK)
        draw_tag(d, x0 + 480, hy2 + 104, "[" + tag + "]")

    # Ten drawn cards, two rows of five. Slot 150 tall, image 58 tall.
    # The text of each card is pasted from its own canvas, so a long line
    # can never cross into the next card.
    gap = 4
    for row in range(2):
        cy = 470 + row * 150
        for col in range(5):
            card = CARDS[row * 5 + col]
            num = card[0]
            x = 12 + col * (CW + gap)
            imc = cover(art(card[7]), CW, 58)
            img.paste(imc, (x, cy))
            text_canvas, widest = render_card_text(card)
            img.paste(text_canvas, (x, cy + 62), text_canvas)
            print("card %d widest text line: %.0f px (limit %d)"
                  % (num, widest, CW))

    # Section headers
    d.text((12, 776), "WHERE IT HAPPENED · 1-13", font=F_MAPHEAD, fill=INK)
    d.text((320, 776), "ALSO ON FRIDAY 20 NOVEMBER", font=F_MAPHEAD, fill=INK)

    # World map, hand drawn, with numbered pins
    mx, my, mw, mh = 12, 790, 288, 144
    for poly in CONTINENTS:
        pts = [(mx + (lon + 180) / 360.0 * mw, my + (90 - lat) / 180.0 * mh)
               for lon, lat in poly]
        d.polygon(pts, fill=MAPFILL)
    for num, lon, lat, dx, dy in PINS:
        px = mx + (lon + 180) / 360.0 * mw + dx
        py = my + (90 - lat) / 180.0 * mh + dy
        d.ellipse([px - 6, py - 6, px + 6, py + 6], fill=RED, outline=PAPER, width=1)
        tw = d.textlength(str(num), font=F_BRIEF_N)
        d.text((px - tw / 2, py - 5), str(num), font=F_BRIEF_N, fill=PAPER)

    # Numbered briefs, two columns, one short line each
    for i, (num, text, src) in enumerate(BRIEFS):
        col = 0 if i < 12 else 1
        bx = 320 + col * 344
        by = 790 + (i % 12) * 12
        ntxt = str(num) + "."
        d.text((bx, by), ntxt, font=F_BRIEF_N, fill=RED)
        txb = bx + d.textlength(ntxt, font=F_BRIEF_N) + 4
        # Trim the text if text plus source would run past the column edge
        avail = (bx + 336) - txb - d.textlength(" " + src, font=F_BRIEF_S) - 2
        shown = text
        while d.textlength(shown, font=F_BRIEF) > avail and len(shown) > 10:
            shown = shown[:-1]
        d.text((txb, by), shown, font=F_BRIEF, fill=INK)
        d.text((txb + d.textlength(shown, font=F_BRIEF) + 4, by), src,
               font=F_BRIEF_S, fill=GREY)

    # DATE CHECK box
    d.rectangle([12, 940, 1000, 984], outline=RED, width=2)
    d.text((20, 944), "DATE CHECK: LEFT OUT ON PURPOSE", font=F_DATECHECK_T, fill=RED)
    dc = ("Thursday 19 November news, not Friday's: the Trump-Xi-Putin declaration "
          "in Shenzhen; the ICJ Myanmar ruling; Anthropic's IPO day; GTA VI's "
          "launch day. Not yet: BepiColombo reaches Mercury on 21 Nov; the COP31 deal.")
    dlines = wrap(d, dc, F_DATECHECK, 984)
    yy = 958
    for ln in dlines:
        d.text((20, yy), ln, font=F_DATECHECK, fill=INK)
        yy += 12

    # Footer
    d.text((12, 990), "Every story here happened, or was first reported, on Friday 20 November 2026.",
           font=F_FOOT, fill=INK)
    d.text((12, 1002), "Sources: Reuters, AP, AFP, BBC, Al Jazeera, IMD, WSJ. Pictures are "
           "AI-generated illustrations. Map drawn in code. HOW SURE: REPORTED means "
           "named sources; CLAIM means one side says so.", font=F_FOOT, fill=INK)

    out = os.path.join(WORK, "entry.png")
    img.save(out, "JPEG", quality=90)
    print("wrote", out, os.path.getsize(out), "bytes")
    return out


if __name__ == "__main__":
    build()
