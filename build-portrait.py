"""Build the owner's portrait for the About section.

    python3 build-portrait.py            report only, writes nothing
    python3 build-portrait.py --apply    write assets/about/

The source is a cut-out -- the subject on transparency -- so it is framed by
the same rule the product cards use: trimmed out of its own padding, then
fitted whole inside the frame with one consistent margin. Nothing of the
subject is cropped.

Two files come out, as everywhere else on this site: a transparent WebP, which
is what the page actually serves, and a cream-flattened JPEG beside it for any
browser that cannot take WebP. The stage is cream-alt, so a portrait flattened
onto plain cream would show a seam against it -- hence the transparent one.

Rerun this only if the photograph is replaced.
"""
import os, sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "source", "owner", "priyanka.png")
OUT = os.path.join(HERE, "assets", "about")
APPLY = "--apply" in sys.argv

SIZE = (760, 950)        # 4:5, the same shape as a product card
CREAM = (250, 246, 240)
FAINT = 4                # alpha below this is invisible haze, not the subject
SPECK = 0.005            # a part holding less of the picture than this is not the subject
KEEP = 0.98
INSET = 8


def alpha_box(im):
    """The subject inside its own file. Same measurement as build-og-images.py:
    getbbox() counts any pixel above zero and background removal leaves a haze
    out to the file edges, so it has to be measured by connected part."""
    a = im.getchannel("A")
    whole = a.getbbox() or (0, 0, im.width, im.height)
    arr = np.asarray(a, dtype=np.int64)
    mask = arr >= FAINT
    if not mask.any():
        return whole
    from scipy import ndimage
    lab, n = ndimage.label(mask)
    ink = ndimage.sum(arr, lab, range(1, n + 1))
    total = ink.sum()
    if not total:
        return whole
    keep = [i + 1 for i, v in enumerate(ink) if v / total >= SPECK]
    if keep and sum(ink[i - 1] for i in keep) / total >= KEEP:
        mask = np.isin(lab, keep)
    ys, xs = np.where(mask)
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def main():
    if not os.path.exists(SRC):
        sys.exit("FAIL  no photograph at %s" % os.path.relpath(SRC, HERE))
    im = Image.open(SRC)
    im.load()
    im = im.convert("RGBA")
    box = alpha_box(im)
    im = im.crop(box)
    tw, th = SIZE
    canvas = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    s = min((tw - INSET * 2) / im.width, (th - INSET * 2) / im.height)
    r = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)
    canvas.paste(r, ((tw - r.width) // 2, (th - r.height) // 2))
    print("source   %dx%d, subject %dx%d" % (
        Image.open(SRC).width, Image.open(SRC).height, box[2] - box[0], box[3] - box[1]))
    print("portrait %dx%d, subject fills %.0f%% of the frame" % (
        tw, th, r.width * r.height / (tw * th) * 100))
    if not APPLY:
        print("\ndry run -- nothing written. add --apply.")
        return
    os.makedirs(OUT, exist_ok=True)
    canvas.save(os.path.join(OUT, "priyanka.webp"), "WEBP", quality=88, method=6)
    flat = Image.new("RGB", SIZE, CREAM)
    flat.paste(canvas, (0, 0), canvas)
    flat.save(os.path.join(OUT, "priyanka.jpg"), quality=86, optimize=True, progressive=True)
    for f in ("priyanka.webp", "priyanka.jpg"):
        print("  %-16s %5.0f KB" % (f, os.path.getsize(os.path.join(OUT, f)) / 1024))


if __name__ == "__main__":
    main()
