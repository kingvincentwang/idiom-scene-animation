"""Draw every mouth in an animation's MOUTHS table onto its scene image, closed / half / full open,
and save one contact sheet, so placement can be checked without playing the animation.

    python check_mouths.py <成語>動畫.html out.jpg

Reads the MOUTHS entries from the HTML and the scene image paths from the <img> tags inside .cam.
Approximates the page's rendering: 'closed' = SVG cartoon mouth whose height grows,
'open' = the original mouth patch stretched downward by `pull`.
"""
import os
import re
import sys
from PIL import Image, ImageDraw, ImageFilter


def quad(p0, p1, p2, n=20):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1])
            for t in (k / n for k in range(n + 1))]


# same outline as the SVG path in the template (viewBox 0 0 100 60)
SHAPE = quad((2, 6), (50, -3), (98, 6)) + quad((98, 6), (86, 60), (50, 60)) + quad((50, 60), (14, 60), (2, 6))


def parse(html):
    block = re.search(r"const MOUTHS=\{(.*?)\n\};", html, re.S)
    if not block:
        sys.exit("MOUTHS table not found")
    mouths = {}
    for key, body in re.findall(r"(\w+)\s*:\{([^}]*)\}", block.group(1)):
        m = dict(re.findall(r"(\w+):\s*'?([\w.]+)'?", body))
        mouths[key] = {k: (v if k == "type" else float(v)) for k, v in m.items()}
    cam = html.split('id="cam"', 1)[1].split("</div>", 1)[0]
    imgs = re.findall(r'<img src="([^"]+)"', cam)
    return mouths, imgs


def render(im, m, o):
    W, H = im.size
    x, y, w, h = m["x"], m["y"], m["w"], m["h"]
    cw = max(w * 3.5, .06)
    box = (int((x - cw / 2) * W), int((y - cw * .7) * H), int((x + cw / 2) * W), int((y + cw * 1.1) * H))
    S = 6
    if m.get("type") == "open" and o:
        box2 = (int((x - w / 2) * W), int(y * H), int((x + w / 2) * W), int((y + h) * H))
        p = im.crop(box2)
        p = p.resize((p.width, int(p.height * (1 + o * m.get("pull", 0)))))
        mask = Image.new("L", p.size, 0)
        ImageDraw.Draw(mask).ellipse([0, 0, p.width, p.height], fill=255)
        im = im.copy()
        im.paste(p, box2[:2], mask.filter(ImageFilter.GaussianBlur(p.width * .12)))
    c = im.crop(box).resize(((box[2] - box[0]) * S, (box[3] - box[1]) * S), Image.LANCZOS)
    if m.get("type") == "closed" and o:
        ox, oy = (x - w / 2) * W - box[0], y * H - box[1]
        mw, mh = w * W, h * H * o
        pts = [((ox + px / 100 * mw) * S, (oy + py / 60 * mh) * S) for px, py in SHAPE]
        lay = Image.new("RGB", c.size, (58, 11, 8))
        d = ImageDraw.Draw(lay)
        d.rectangle([0, 0, c.width, (oy + 16 / 60 * mh) * S], fill=(243, 234, 216))
        d.ellipse([(ox + .2 * mw) * S, (oy + mh * 42 / 60) * S, (ox + .8 * mw) * S, (oy + mh * 82 / 60) * S],
                  fill=(180, 75, 66))
        mask = Image.new("L", c.size, 0)
        ImageDraw.Draw(mask).polygon(pts, fill=255)
        c.paste(lay, (0, 0), mask)
        ImageDraw.Draw(c).line(pts, fill=(180, 87, 78), width=max(2, int(S * .6)))
    return c.resize((240, int(240 * c.height / c.width)))


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    html_path, out = sys.argv[1], sys.argv[2]
    base = os.path.dirname(os.path.abspath(html_path))
    mouths, imgs = parse(open(html_path, encoding="utf-8").read())
    tiles = []
    for key, m in mouths.items():
        im = Image.open(os.path.join(base, imgs[int(m["img"])])).convert("RGB")
        for o in (0, .5, 1):
            t = render(im, m, o)
            ImageDraw.Draw(t).text((3, 3), f"{key} {o}", fill=(255, 255, 0))
            tiles.append(t)
    th = max(t.height for t in tiles)
    sheet = Image.new("RGB", (720, th * len(mouths)))
    for n, t in enumerate(tiles):
        sheet.paste(t, ((n % 3) * 240, (n // 3) * th))
    sheet.save(out)
    print(out)


if __name__ == "__main__":
    main()
