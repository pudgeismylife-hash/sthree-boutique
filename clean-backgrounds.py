"""Cut the flat white background off the pieces that still sit in a box.

    python3 clean-backgrounds.py            report only, writes nothing
    python3 clean-backgrounds.py --apply    rewrite the files listed below

The viewer's stage is cream-alt, #F3EDE4. A picture whose own background is
white paints a bright rectangle on that cream, and the piece reads as pasted on
rather than photographed -- which is exactly what a customer sees on the anklet
and the bracelet today.

Only pictures whose background really is a flat, near-white field are touched,
and only those named in TARGETS. A photograph with a real backdrop -- the earrings
on silk, the nail sets on grey card -- is left alone: that background is part of
the picture, and cutting it out would leave a floating object with a bitten edge.

The cut is a flood fill inwards from the border, not a threshold on the whole
frame. A threshold would eat every pale part of the piece as well: the pave
stones on the anklet, the pearl on the ring, the white of a nail. Only
background that is connected to the edge of the frame goes.
"""
import json, os, sys
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "assets", "products")
APPLY = "--apply" in sys.argv

CREAM = (250, 246, 240)
TOL = 26            # how far from the border colour still counts as background
FEATHER = 0.8       # px of blur on the cut edge, so it is not a staircase
HOLE = 0.004        # an enclosed background field must be this much of the frame

# file stem -> why this one
TARGETS = {
    "anklets_2-a1": "her second anklet, on pure white -- the brightest box on the site",
    "anklets_2-a2": "same piece, second view",
    "anklets_2-a3": "same piece, third view",
    "bracelet_1-a1": "the evil eye bracelet, on near-white",
    "bracelet_1-a2": "same piece, second view",
    "bracelet_1-a3": "same piece, third view",
    "armcuff_2-a1": "the sculpted floral armcuff, on flat grey-white",
    "armcuff_2-a2": "same piece, second view",
    "armcuff_2-a3": "same piece, third view",
    "armcuff_1-a2": "the worn view of the butterfly armcuff, shot on white",
}


def cut(path):
    """Alpha for the piece, with the border-connected background removed."""
    im = Image.open(path).convert("RGB")
    a = np.asarray(im).astype(np.int16)

    border = np.concatenate([a[0, :, :], a[-1, :, :], a[:, 0, :], a[:, -1, :]])
    bg = np.median(border, axis=0)
    if not (bg > 235).all():
        return None, im, bg, 0       # not a white field; leave it alone

    near = (np.abs(a - bg).max(axis=2) <= TOL)

    lab, n = ndimage.label(near)
    edge = set(lab[0, :]) | set(lab[-1, :]) | set(lab[:, 0]) | set(lab[:, -1])
    edge.discard(0)
    drop = set(edge)

    # A chain closes a loop, and the background inside that loop touches no edge
    # of the frame, so a fill from the border leaves a white pool sitting in the
    # middle of the anklet. Enclosed background counts too -- but only when it is
    # a real field. The threshold is what separates the inside of a bracelet from
    # a specular highlight on gold, which is also near-white and must stay.
    if n:
        sizes = ndimage.sum(np.ones_like(lab), lab, index=range(1, n + 1))
        floor = HOLE * a.shape[0] * a.shape[1]
        holes = [i + 1 for i, s in enumerate(sizes) if s >= floor and (i + 1) not in edge]
        drop |= set(holes)
    else:
        holes = []

    outside = np.isin(lab, list(drop)) if drop else np.zeros(lab.shape, bool)
    alpha = np.where(outside, 0, 255).astype(np.uint8)
    m = Image.fromarray(alpha).filter(ImageFilter.GaussianBlur(FEATHER))
    return m, im, bg, len(holes)


def main():
    lock_hint = []
    done = skipped = 0
    for stem, why in TARGETS.items():
        p = os.path.join(OUT, stem + ".jpg")
        if not os.path.exists(p):
            print("  MISS %-18s no such file" % stem)
            continue
        mask, im, bg, holes = cut(p)
        if mask is None:
            print("  SKIP %-18s background is %s, not a white field" % (
                stem, tuple(int(x) for x in bg)))
            skipped += 1
            continue
        kept = np.asarray(mask).mean() / 255
        print("%-18s %-11s bg=%s  piece is %.0f%% of the frame%s" % (
            stem, "%dx%d" % im.size, tuple(int(x) for x in bg), kept * 100,
            ", %d enclosed field(s) cleared" % holes if holes else ""))
        print("                   %s" % why)
        if kept > 0.92:
            print("                   REFUSED: almost nothing was cut, the fill "
                  "did not find an edge")
            skipped += 1
            continue
        if APPLY:
            rgba = im.convert("RGBA")
            rgba.putalpha(mask)
            rgba.save(os.path.join(OUT, stem + ".webp"), "WEBP", quality=90, method=6)
            flat = Image.new("RGB", im.size, CREAM)
            flat.paste(im, mask=mask)
            flat.save(p, quality=88, optimize=True, progressive=True)
        done += 1
        lock_hint.append(stem)

    # A product marked alpha:true has every one of its views fetched as .webp,
    # so a sibling view this script skipped -- the worn shot, the close-up --
    # must still have a .webp beside it or the gallery asks for a file that was
    # never written. Those are copied across as they are, opaque.
    for key in sorted({s.rsplit("-a", 1)[0] for s in lock_hint}):
        n = 1
        while True:
            sib = os.path.join(OUT, "%s-a%d.jpg" % (key, n))
            if not os.path.exists(sib):
                break
            web = sib[:-4] + ".webp"
            if not os.path.exists(web):
                print("  also  %-16s carried across as opaque webp" % os.path.basename(sib))
                if APPLY:
                    Image.open(sib).convert("RGBA").save(web, "WEBP", quality=90, method=6)
            n += 1

    print("\n%d file(s)%s, %d skipped" % (done, "" if APPLY else " would be cut", skipped))
    if done and not APPLY:
        print("dry run -- nothing written. add --apply.")
    if done:
        keys = sorted({s.rsplit("-a", 1)[0] for s in lock_hint})
        print("set alpha:true on: " + ", ".join(keys))


if __name__ == "__main__":
    main()
