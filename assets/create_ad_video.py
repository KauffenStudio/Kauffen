#!/usr/bin/env python3
"""iStarTec Google Ads Video — V3 Premium with service illustrations & fluid animations"""

import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from moviepy import VideoClip

# ── Config ──────────────────────────────────────────────────────────────
W, H = 1920, 1080
FPS = 30
DURATION = 15  # longer for showcase scenes
OUTPUT = "/Users/augustinagapii/Desktop/IStarTec/assets/istartec-ad.mp4"

# Brand colors
BLUE = (37, 99, 235)
BLUE_DARK = (30, 64, 175)
BLUE_DEEP = (15, 23, 42)
BLUE_MID = (25, 45, 120)
WHITE = (255, 255, 255)
LIGHT_GRAY = (241, 245, 249)
ACCENT = (96, 165, 250)
CYAN = (56, 189, 248)
WARM = (251, 191, 36)  # gold/warm accent for highlights


# ── Fonts ───────────────────────────────────────────────────────────────
def get_font(size, bold=False):
    candidates = [
        "/System/Library/Fonts/SFPro-Bold.otf" if bold else "/System/Library/Fonts/SFPro-Regular.otf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


# ── Easing ──────────────────────────────────────────────────────────────
def ease_out_cubic(t):
    return 1 - (1 - t) ** 3

def ease_out_back(t):
    """Overshoots slightly then settles — bouncy feel."""
    c1 = 1.70158
    return 1 + (c1 + 1) * ((t - 1) ** 3) + c1 * ((t - 1) ** 2)

def ease_in_out(t):
    return 3 * t**2 - 2 * t**3

def ease_out_elastic(t):
    """Spring-like bounce."""
    if t == 0 or t == 1:
        return t
    return 2 ** (-10 * t) * math.sin((t - 0.075) * (2 * math.pi) / 0.3) + 1

def clamp(v, lo=0.0, hi=1.0):
    return max(lo, min(hi, v))


# ── Drawing primitives ──────────────────────────────────────────────────
def draw_gradient_bg(draw, w, h, c_top, c_bot):
    for y in range(h):
        r = y / h
        draw.line([(0, y), (w, y)], fill=tuple(
            int(c_top[i] + (c_bot[i] - c_top[i]) * r) for i in range(3)))

def draw_radial_gradient(img, cx, cy, radius, color, alpha=50):
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for i in range(radius, 0, -3):
        a = int(alpha * ((i / radius) ** 0.6))
        od.ellipse([cx - i, cy - i, cx + i, cy + i], fill=(*color, a))
    bg = img.convert("RGBA")
    return Image.alpha_composite(bg, overlay).convert("RGB")

def draw_star(draw, cx, cy, size, color, rotation=0):
    pts = []
    for i in range(10):
        angle = math.radians(rotation + i * 36 - 90)
        r = size if i % 2 == 0 else size * 0.4
        pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    draw.polygon(pts, fill=color)

def get_tw(draw, text, font):
    bb = draw.textbbox((0, 0), text, font=font)
    return bb[2] - bb[0]

def add_particles(img, frame, n=40, seed=42):
    rng = np.random.RandomState(seed)
    draw = ImageDraw.Draw(img)
    for i in range(n):
        bx, by = rng.randint(0, W), rng.randint(0, H)
        oy = math.sin(frame * 0.025 + i * 1.7) * 25
        ox = math.cos(frame * 0.018 + i * 2.3) * 15
        x = bx + ox
        y = (by + oy + frame * 0.4) % H
        sz = rng.uniform(1, 4)
        draw.ellipse([x - sz, y - sz, x + sz, y + sz], fill=ACCENT)
    return img

def draw_water_drops(draw, cx, cy, frame, count=5):
    """Animated water drops falling."""
    for i in range(count):
        offset = (frame * 2 + i * 40) % 120
        dy = offset - 20
        alpha_f = 1.0 - clamp(offset / 120)
        if dy < 0:
            continue
        dx = math.sin(i * 2.1) * 15
        sz = 4 + i % 3
        # Teardrop shape
        color = tuple(int(c * alpha_f + BLUE_DEEP[j] * (1 - alpha_f)) for j, c in enumerate(CYAN))
        draw.ellipse([cx + dx - sz, cy + dy - sz, cx + dx + sz, cy + dy + sz], fill=color)
        # small tail
        draw.polygon([
            (cx + dx - sz * 0.5, cy + dy - sz),
            (cx + dx + sz * 0.5, cy + dy - sz),
            (cx + dx, cy + dy - sz * 2.5)
        ], fill=color)


# ── Service illustration icons (drawn with PIL) ────────────────────────

def draw_pipe_icon(draw, cx, cy, size, color, frame=0):
    """Plumbing pipes with flowing water animation."""
    s = size
    # Horizontal pipe
    draw.rounded_rectangle([cx - s, cy - s*0.15, cx + s*0.3, cy + s*0.15], radius=4, fill=color)
    # Vertical pipe
    draw.rounded_rectangle([cx + s*0.15, cy - s, cx + s*0.45, cy + s*0.15], radius=4, fill=color)
    # Elbow joint
    draw.ellipse([cx + s*0.05, cy - s*0.25, cx + s*0.55, cy + s*0.25], fill=color)
    # Wrench
    wx, wy = cx - s * 0.5, cy + s * 0.3
    draw.rounded_rectangle([wx, wy, wx + s*0.8, wy + s*0.12], radius=3, fill=ACCENT)
    draw.ellipse([wx + s*0.6, wy - s*0.08, wx + s*1.0, wy + s*0.2], outline=ACCENT, width=3)
    # Water drops
    drop_offset = (frame * 3) % 30
    for i in range(3):
        dy = (drop_offset + i * 10) % 30
        a = 1.0 - dy / 30
        dc = tuple(int(CYAN[j] * a + BLUE_DEEP[j] * (1 - a)) for j in range(3))
        draw.ellipse([cx - s - 8 + i*4, cy + s*0.2 + dy, cx - s - 2 + i*4, cy + s*0.2 + dy + 5], fill=dc)

def draw_radiator_icon(draw, cx, cy, size, color, frame=0):
    """Underfloor heating / radiator."""
    s = size
    # Floor base
    draw.rounded_rectangle([cx - s, cy + s*0.4, cx + s, cy + s*0.55], radius=3, fill=(40, 60, 100))
    # Wavy heating pipes under floor
    for i in range(5):
        x_off = cx - s * 0.8 + i * s * 0.4
        wave = math.sin(frame * 0.08 + i) * 4
        draw.arc([x_off, cy - s*0.1 + wave, x_off + s*0.35, cy + s*0.35 + wave],
                 0, 180, fill=color, width=3)
    # Heat waves rising
    for i in range(3):
        wave_y = cy - s * 0.2 - ((frame * 1.5 + i * 20) % 40)
        wave_x = cx - s * 0.3 + i * s * 0.3
        opacity_f = 1.0 - ((frame * 1.5 + i * 20) % 40) / 40
        hc = tuple(int(WARM[j] * opacity_f + BLUE_DEEP[j] * (1 - opacity_f)) for j in range(3))
        draw.arc([wave_x - 8, wave_y, wave_x + 8, wave_y + 12], 180, 0, fill=hc, width=2)
        draw.arc([wave_x - 5, wave_y - 8, wave_x + 5, wave_y + 4], 0, 180, fill=hc, width=2)

def draw_solar_icon(draw, cx, cy, size, color, frame=0):
    """Solar thermal panel with sun."""
    s = size
    # Panel (tilted rectangle)
    pts = [
        (cx - s*0.7, cy + s*0.3),
        (cx - s*0.4, cy - s*0.5),
        (cx + s*0.7, cy - s*0.5),
        (cx + s*0.4, cy + s*0.3),
    ]
    draw.polygon(pts, fill=color)
    # Grid lines on panel
    for i in range(1, 4):
        f = i / 4
        lx1 = pts[0][0] + (pts[3][0] - pts[0][0]) * f
        ly1 = pts[0][1] + (pts[3][1] - pts[0][1]) * f
        lx2 = pts[1][0] + (pts[2][0] - pts[1][0]) * f
        ly2 = pts[1][1] + (pts[2][1] - pts[1][1]) * f
        draw.line([(lx1, ly1), (lx2, ly2)], fill=BLUE_MID, width=2)
    # Sun
    sun_x = cx + s * 0.9
    sun_y = cy - s * 0.6
    ray_len = 12 + 3 * math.sin(frame * 0.1)
    draw.ellipse([sun_x - 12, sun_y - 12, sun_x + 12, sun_y + 12], fill=WARM)
    for a in range(0, 360, 45):
        rad = math.radians(a + frame * 2)
        draw.line([
            (sun_x + 16 * math.cos(rad), sun_y + 16 * math.sin(rad)),
            (sun_x + ray_len * math.cos(rad) + 5, sun_y + ray_len * math.sin(rad) + 5),
        ], fill=WARM, width=2)

def draw_drain_icon(draw, cx, cy, size, color, frame=0):
    """Drainage / water system."""
    s = size
    # Pipe sections
    draw.rounded_rectangle([cx - s*0.1, cy - s*0.7, cx + s*0.1, cy], radius=3, fill=color)
    draw.rounded_rectangle([cx - s*0.1, cy - s*0.1, cx + s*0.7, cy + s*0.1], radius=3, fill=color)
    draw.rounded_rectangle([cx + s*0.5, cy - s*0.1, cx + s*0.7, cy + s*0.5], radius=3, fill=color)
    # Joints
    draw.ellipse([cx - s*0.18, cy - s*0.18, cx + s*0.18, cy + s*0.18], fill=ACCENT)
    draw.ellipse([cx + s*0.42, cy - s*0.18, cx + s*0.78, cy + s*0.18], fill=ACCENT)
    # Water flowing
    for i in range(4):
        offset = (frame * 2 + i * 15) % 60
        wx = cx + offset * s * 0.01
        wy = cy
        if wx < cx + s * 0.5:
            draw.ellipse([wx - 3, wy - 3, wx + 3, wy + 3], fill=CYAN)


# ── Scene renderers ─────────────────────────────────────────────────────

def scene_intro(frame, local_frames):
    """0-3s: Cinematic logo reveal."""
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    draw_gradient_bg(draw, W, H, BLUE_DEEP, (8, 12, 30))
    t = frame / local_frames

    # Multiple glow layers for depth
    glow_pulse = int(180 + 30 * math.sin(frame * 0.08))
    img = draw_radial_gradient(img, W//2, H//2 - 50, glow_pulse, BLUE, alpha=40)
    img = draw_radial_gradient(img, W//2 - 200, H//2 + 100, 120, ACCENT, alpha=15)
    img = draw_radial_gradient(img, W//2 + 250, H//2 - 150, 100, CYAN, alpha=12)
    draw = ImageDraw.Draw(img)

    # Animated grid lines in background
    for i in range(0, W, 120):
        line_alpha = 0.05 + 0.03 * math.sin(frame * 0.02 + i * 0.01)
        lc = tuple(int(ACCENT[j] * line_alpha) for j in range(3))
        draw.line([(i, 0), (i, H)], fill=lc, width=1)
    for i in range(0, H, 120):
        line_alpha = 0.05 + 0.03 * math.sin(frame * 0.02 + i * 0.01)
        lc = tuple(int(ACCENT[j] * line_alpha) for j in range(3))
        draw.line([(0, i), (W, i)], fill=lc, width=1)

    # Star with elastic bounce
    star_t = clamp(t * 2.5)
    star_p = ease_out_elastic(star_t) if star_t > 0 else 0
    star_size = int(70 * star_p)
    star_rot = (1 - ease_out_cubic(star_t)) * 360

    if star_size > 2:
        cx, cy = W // 2, H // 2 - 70
        sq = int(95 * star_p)
        # Outer glow square
        draw.rounded_rectangle([cx - sq - 6, cy - sq - 6, cx + sq + 6, cy + sq + 6],
                              radius=24, fill=BLUE_DARK)
        draw.rounded_rectangle([cx - sq, cy - sq, cx + sq, cy + sq],
                              radius=20, fill=BLUE)
        draw_star(draw, cx, cy, star_size, WHITE, rotation=star_rot)

    # Brand text with letter-by-letter reveal
    text_t = clamp((t - 0.25) * 2.5)
    if text_t > 0:
        font_big = get_font(95, bold=True)
        font_sub = get_font(34)
        text_y = int(H // 2 + 55 + 50 * (1 - ease_out_cubic(text_t)))

        parts = [("i", WHITE), ("Star", ACCENT), ("Tec", WHITE)]
        total_w = sum(get_tw(draw, p[0], font_big) for p in parts)
        x = (W - total_w) // 2

        for pi, (txt, col) in enumerate(parts):
            char_t = clamp((text_t - pi * 0.08) * 2)
            if char_t > 0:
                cp = ease_out_back(char_t)
                char_y = text_y + int(15 * (1 - cp))
                draw.text((x, char_y), txt, fill=col, font=font_big)
            x += get_tw(draw, txt, font_big)

        # Subtitle with slide
        sub_t = clamp((t - 0.4) * 2.5)
        if sub_t > 0:
            sp = ease_out_cubic(sub_t)
            subtitle = "Instalações Hidráulicas Profissionais"
            sw = get_tw(draw, subtitle, font_sub)
            sy = int(text_y + 115 + 30 * (1 - sp))
            draw.text(((W - sw) // 2, sy), subtitle, fill=LIGHT_GRAY, font=font_sub)

            # Animated accent line
            line_w = int(250 * sp)
            draw.line([(W//2 - line_w, sy + 50), (W//2 + line_w, sy + 50)],
                     fill=ACCENT, width=3)

        # "Algarve, Portugal" badge
        badge_t = clamp((t - 0.55) * 3)
        if badge_t > 0:
            bp = ease_out_cubic(badge_t)
            font_badge = get_font(24)
            badge = "ALGARVE  •  PORTUGAL"
            bw = get_tw(draw, badge, font_badge)
            by = int(text_y + 185 + 20 * (1 - bp))
            # Badge background
            pad = 20
            draw.rounded_rectangle([(W - bw)//2 - pad, by - 6,
                                    (W + bw)//2 + pad, by + 30],
                                   radius=15, fill=BLUE_DARK)
            draw.text(((W - bw) // 2, by), badge, fill=ACCENT, font=font_badge)

    img = add_particles(img, frame)
    return np.array(img)


def scene_services_showcase(frame, local_frames):
    """3-8s: Service cards with animated illustrations."""
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    draw_gradient_bg(draw, W, H, BLUE_DEEP, (8, 12, 30))
    t = frame / local_frames

    # Subtle ambient glows
    img = draw_radial_gradient(img, 300, 600, 200, BLUE, alpha=20)
    img = draw_radial_gradient(img, W - 300, 400, 180, ACCENT, alpha=15)
    draw = ImageDraw.Draw(img)

    # Title
    font_title = get_font(50, bold=True)
    title_t = ease_out_cubic(clamp(t * 5))
    title = "Os Nossos Serviços"
    tw = get_tw(draw, title, font_title)
    tx = int((W - tw) / 2)
    ty = 55
    draw.text((tx, ty), title, fill=WHITE, font=font_title)
    # Title underline
    lw = int(180 * title_t)
    draw.line([(W//2 - lw, ty + 65), (W//2 + lw, ty + 65)], fill=ACCENT, width=3)

    # 4 large service cards with illustrations
    services = [
        ("Canalização &\nReparações", draw_pipe_icon, BLUE),
        ("Piso Radiante\nHidráulico", draw_radiator_icon, BLUE),
        ("Solar\nTérmico", draw_solar_icon, BLUE),
        ("Drenagem &\nVentilação", draw_drain_icon, BLUE),
    ]

    card_w, card_h = 380, 340
    gap = 40
    total_cards_w = card_w * 4 + gap * 3
    sx = (W - total_cards_w) // 2
    sy = 160

    font_svc = get_font(26, bold=True)

    for i, (label, icon_fn, icon_color) in enumerate(services):
        delay = 0.05 + i * 0.08
        card_t = clamp((t - delay) * 3)
        if card_t <= 0:
            continue

        cp = ease_out_back(card_t)
        cx = sx + i * (card_w + gap) + card_w // 2
        cy_card = sy + card_h // 2

        # Scale + slide up
        y_off = int(80 * (1 - cp))
        scale = 0.8 + 0.2 * cp

        # Card background with gradient feel
        card_top = cy_card - int(card_h * scale / 2) + y_off
        card_bot = cy_card + int(card_h * scale / 2) + y_off
        card_left = cx - int(card_w * scale / 2)
        card_right = cx + int(card_w * scale / 2)

        # Card shadow
        draw.rounded_rectangle([card_left + 4, card_top + 4, card_right + 4, card_bot + 4],
                              radius=20, fill=(5, 10, 25))
        # Card body
        draw.rounded_rectangle([card_left, card_top, card_right, card_bot],
                              radius=20, fill=(18, 35, 75))
        # Card border glow
        draw.rounded_rectangle([card_left, card_top, card_right, card_bot],
                              radius=20, outline=BLUE, width=2)

        # Icon illustration (animated)
        icon_cy = card_top + int(card_h * 0.38)
        icon_fn(draw, cx, icon_cy, 55, ACCENT, frame)

        # Service label
        lines = label.split("\n")
        for li, line in enumerate(lines):
            lw_text = get_tw(draw, line, font_svc)
            draw.text((cx - lw_text // 2, card_bot - 85 + li * 32), line,
                     fill=WHITE, font=font_svc)

    # Bottom service list (smaller text, the remaining services)
    extra_t = clamp((t - 0.5) * 2.5)
    if extra_t > 0:
        ep = ease_out_cubic(extra_t)
        font_extra = get_font(22)
        extras = "Redes de Água  •  Esgotos  •  Condensados AC  •  Coletores Hidráulicos"
        ew = get_tw(draw, extras, font_extra)
        ey = int(sy + card_h + 70 + 20 * (1 - ep))
        # Background bar
        draw.rounded_rectangle([(W - ew)//2 - 30, ey - 8, (W + ew)//2 + 30, ey + 32],
                              radius=16, fill=BLUE_DARK)
        draw.text(((W - ew) // 2, ey), extras, fill=LIGHT_GRAY, font=font_extra)

    img = add_particles(img, frame, n=25)
    return np.array(img)


def scene_trust(frame, local_frames):
    """8-11s: Stats + certifications with counter animation."""
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    draw_gradient_bg(draw, W, H, BLUE_DEEP, (8, 12, 30))
    t = frame / local_frames

    img = draw_radial_gradient(img, W//2, H//2 - 30, 300, BLUE, alpha=30)
    draw = ImageDraw.Draw(img)

    font_num = get_font(80, bold=True)
    font_label = get_font(26)
    font_partner_title = get_font(32, bold=True)
    font_partner = get_font(28)

    stats = [
        ("+25", "Anos de Experiência", ACCENT),
        ("+100", "Projetos Concluídos", CYAN),
        ("100%", "Satisfação do Cliente", WARM),
    ]

    card_w = 440
    gap = 50
    total_w = card_w * 3 + gap * 2
    start_x = (W - total_w) // 2

    for i, (num, label, highlight) in enumerate(stats):
        delay = i * 0.1
        card_t = clamp((t - delay) * 2.8)
        if card_t <= 0:
            continue

        cp = ease_out_back(card_t)
        cx = start_x + i * (card_w + gap) + card_w // 2
        cy = H // 2 - 80
        y_off = int(70 * (1 - cp))

        # Card shadow
        draw.rounded_rectangle([cx - card_w//2 + 5, cy - 105 + y_off + 5,
                                cx + card_w//2 + 5, cy + 105 + y_off + 5],
                              radius=22, fill=(5, 10, 25))
        # Card
        draw.rounded_rectangle([cx - card_w//2, cy - 105 + y_off,
                                cx + card_w//2, cy + 105 + y_off],
                              radius=22, fill=(18, 35, 75))
        # Top accent bar
        draw.rounded_rectangle([cx - card_w//2, cy - 105 + y_off,
                                cx + card_w//2, cy - 95 + y_off],
                              radius=22, fill=highlight)

        # Animated number counter
        if card_t < 0.7:
            # Count up effect
            count_t = card_t / 0.7
            if num.startswith("+"):
                n_val = int(num[1:])
                display = f"+{int(n_val * count_t)}"
            elif num.endswith("%"):
                n_val = int(num[:-1])
                display = f"{int(n_val * count_t)}%"
            else:
                display = num
        else:
            display = num

        nw = get_tw(draw, display, font_num)
        draw.text((cx - nw//2, cy - 75 + y_off), display, fill=highlight, font=font_num)

        lw = get_tw(draw, label, font_label)
        draw.text((cx - lw//2, cy + 35 + y_off), label, fill=LIGHT_GRAY, font=font_label)

    # Partner section
    pt = clamp((t - 0.45) * 2.5)
    if pt > 0:
        pp = ease_out_cubic(pt)
        py = int(H // 2 + 145 + 30 * (1 - pp))

        ptitle = "Parceiros Certificados"
        ptw = get_tw(draw, ptitle, font_partner_title)
        draw.text(((W - ptw) // 2, py), ptitle, fill=WHITE, font=font_partner_title)

        # Partner badges
        partners = ["Bosch", "Uponor", "Grundfos"]
        badge_font = get_font(26, bold=True)
        badge_gap = 40
        badge_w = 180
        total_bw = badge_w * len(partners) + badge_gap * (len(partners) - 1)
        bx = (W - total_bw) // 2

        for pi, pname in enumerate(partners):
            b_t = clamp((pt - 0.1 - pi * 0.08) * 4)
            if b_t <= 0:
                continue
            bp = ease_out_cubic(b_t)
            by = py + 50
            # Badge bg
            draw.rounded_rectangle([bx, by, bx + badge_w, by + 45],
                                  radius=10, fill=BLUE_DARK, outline=ACCENT, width=1)
            pw_text = get_tw(draw, pname, badge_font)
            draw.text((bx + (badge_w - pw_text) // 2, by + 8), pname,
                     fill=ACCENT, font=badge_font)
            bx += badge_w + badge_gap

    img = add_particles(img, frame, n=20)
    return np.array(img)


def scene_cta(frame, local_frames):
    """11-15s: Final CTA with energy."""
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    # Animated gradient shift
    shift = math.sin(frame * 0.04) * 0.15
    c_top = tuple(int(BLUE_DARK[i] * (1 + shift)) for i in range(3))
    draw_gradient_bg(draw, W, H, c_top, BLUE)
    t = frame / local_frames

    # Multiple glow layers
    pulse = 1 + 0.08 * math.sin(frame * 0.12)
    img = draw_radial_gradient(img, W//2, H//2 - 30, int(350 * pulse), WHITE, alpha=18)
    img = draw_radial_gradient(img, W//2 - 300, H - 200, 150, ACCENT, alpha=12)
    img = draw_radial_gradient(img, W//2 + 350, 200, 120, CYAN, alpha=10)
    draw = ImageDraw.Draw(img)

    font_cta = get_font(62, bold=True)
    font_info = get_font(38, bold=True)
    font_web = get_font(32)
    font_brand = get_font(46, bold=True)

    main_t = ease_out_cubic(clamp(t * 3))

    # Logo at top
    if main_t > 0:
        logo_y = int(H//2 - 220 + 50 * (1 - main_t))
        star_sz = int(40 * main_t)
        sq = int(55 * main_t)
        cx = W // 2
        draw.rounded_rectangle([cx - sq - 4, logo_y - sq - 4, cx + sq + 4, logo_y + sq + 4],
                              radius=16, fill=(255, 255, 255, 30))
        draw.rounded_rectangle([cx - sq, logo_y - sq, cx + sq, logo_y + sq],
                              radius=14, fill=BLUE)
        draw_star(draw, cx, logo_y, star_sz, WHITE)

        parts = [("i", WHITE), ("Star", (200, 225, 255)), ("Tec", WHITE)]
        tbw = sum(get_tw(draw, p[0], font_brand) for p in parts)
        bx = (W - tbw) // 2
        by = logo_y + sq + 25
        for txt, col in parts:
            draw.text((bx, by), txt, fill=col, font=font_brand)
            bx += get_tw(draw, txt, font_brand)

    # CTA button
    cta_t = ease_out_back(clamp((t - 0.12) * 2.8))
    if cta_t > 0:
        cta_text = "Peça o Seu Orçamento Gratuito"
        cta_w = get_tw(draw, cta_text, font_cta)
        cta_y = int(H//2 + 20 + 40 * (1 - cta_t))

        # Button background with pulse
        btn_pulse = 1 + 0.03 * math.sin(frame * 0.15)
        pad_x = int(50 * btn_pulse)
        pad_y = int(18 * btn_pulse)
        draw.rounded_rectangle([
            (W - cta_w)//2 - pad_x, cta_y - pad_y,
            (W + cta_w)//2 + pad_x, cta_y + 65 + pad_y
        ], radius=35, fill=WHITE)
        draw.text(((W - cta_w) // 2, cta_y), cta_text, fill=BLUE_DARK, font=font_cta)

    # Contact info
    info_t = ease_out_cubic(clamp((t - 0.3) * 2.5))
    if info_t > 0:
        info_y = int(H//2 + 130 + 25 * (1 - info_t))

        phone = "+351 965 445 801"
        pw = get_tw(draw, phone, font_info)
        draw.text(((W - pw) // 2, info_y), phone, fill=WHITE, font=font_info)

        web = "istartec.co"
        ww = get_tw(draw, web, font_web)
        draw.text(((W - ww) // 2, info_y + 55), web, fill=LIGHT_GRAY, font=font_web)

        loc = "Algarve, Portugal"
        lw = get_tw(draw, loc, font_web)
        draw.text(((W - lw) // 2, info_y + 100), loc, fill=LIGHT_GRAY, font=font_web)

    img = add_particles(img, frame, n=35)
    return np.array(img)


# ── Timeline & transitions ──────────────────────────────────────────────
SCENES = [
    (0, 3.0, scene_intro),
    (3.0, 8.0, scene_services_showcase),
    (8.0, 11.0, scene_trust),
    (11.0, 15.0, scene_cta),
]
FADE = 0.5


def make_frame(t):
    current = None
    nxt = None
    fade_p = 0

    for i, (start, end, renderer) in enumerate(SCENES):
        if start <= t < end:
            lf = int((t - start) * FPS)
            lt = int((end - start) * FPS)
            current = (renderer, lf, lt)
            if t >= end - FADE and i + 1 < len(SCENES):
                fade_p = (t - (end - FADE)) / FADE
                ns, ne, nr = SCENES[i + 1]
                nxt = (nr, 0, int((ne - ns) * FPS))
            break

    if current is None:
        s, e, r = SCENES[-1]
        current = (r, int((e - s) * FPS) - 1, int((e - s) * FPS))

    fa = current[0](current[1], current[2])
    if nxt and fade_p > 0:
        fb = nxt[0](nxt[1], nxt[2])
        a = ease_in_out(fade_p)
        return (fa * (1 - a) + fb * a).astype(np.uint8)
    return fa


if __name__ == "__main__":
    print("🎬 Generating iStarTec premium ad video v3...")
    clip = VideoClip(make_frame, duration=DURATION)
    clip.write_videofile(OUTPUT, fps=FPS, codec="libx264", preset="medium",
                        bitrate="10000k", audio=False, logger="bar")
    print(f"✅ Done: {OUTPUT}")
