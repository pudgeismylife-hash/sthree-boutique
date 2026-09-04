THE FRONT PAGE PICTURE
======================

The hero is one picture running the full width of the screen with the
boutique's name and the WhatsApp button laid over it.

Two files control it, and neither needs any code changed:

  hero-still.jpg   the photograph. Always shown.
  hero.mp4         a film, if there ever is one. Plays over the still.

Replace hero-still.jpg and the front page changes. That is the whole job.


-------------------------------------------------------------------
SHOOTING THE PHOTOGRAPH
-------------------------------------------------------------------

A phone is fine. Portrait mode off, flash off, clean lens.

1. TURN THE PHONE SIDEWAYS.
   Landscape, not upright. The hero is a wide band. An upright photo gets
   cropped hard at the top and bottom and you lose most of it.

2. LEAVE THE LEFT SIDE EMPTY.
   The words sit over the lower left. Put the model on the RIGHT of the
   frame and let the left be street, wall, cloth, sky -- anything quiet.
   If the model stands in the middle, the words land on her face.

3. KEEP THE FACE HIGH IN THE FRAME.
   The picture is cropped from 22% down. A face in the top third
   survives. A face in the middle is fine. A face low in the frame gets
   cut off, which is what happened with the last one.

4. LIGHT FROM THE FRONT OR THE SIDE, NEVER FROM BEHIND.
   Shooting into the sun turns the clothes into a silhouette. Early
   morning or an hour before sunset is the easy answer; an open doorway
   with the light coming in also works.

5. SHOW THE CLOTHES, NOT THE PLACE.
   Close enough that the fabric and the work on it can be seen. A wide
   street shot with a small figure in it sells the street.

6. HOLD STILL AND TAKE TEN.
   Same setup, small changes. Pick the sharpest afterwards. Blur that
   looks acceptable on a phone screen is obvious across a laptop.


-------------------------------------------------------------------
THE FILE
-------------------------------------------------------------------

  Name it exactly       hero-still.jpg
  Landscape             wider than it is tall
  At least              2000 pixels across, 2500 or more is better
  Under about           600 KB after saving, or the page loads slowly

Do not add a border, a frame or a cream margin. The picture must reach
all four edges -- the site puts its own darkening over the bottom so the
words stay readable, and a margin shows as a pale band down the sides.

WHAT IS ON THERE NOW, AND WHY IT IS TEMPORARY
---------------------------------------------

Nothing the boutique has sent is the right shape for a hero: every
photograph is one figure, upright, on a cream studio background. Cropped
to a wide band, they either lose the head or show cream down both sides.

So the picture there now was built rather than shot. It is four of the
boutique's own catalogue photographs -- the black shirt dress, the pink
zari saree, the black sequin saree and the orange floral saree -- cut off
their backgrounds and stood together on a dark warm ground at different
sizes, so the eye reads them as a group. Nothing about any garment was
changed: no colour, no shape, no work invented. It is an arrangement of
real photographs.

  python3 build-hero.py            report only, writes nothing
  python3 build-hero.py --apply    rebuild it

Change which pieces appear by editing FIGURES at the top of build-hero.py.
It refuses to write if a figure would land under the words, above the crop
line, or outside what a phone can see.

It is a stand-in and it is meant to be replaced. One real photograph of
the shop, shot to the rules above, will say more than four cut-outs on a
made-up background ever will -- and dropping hero-still.jpg in place of
this one needs no code changed at all.


-------------------------------------------------------------------
IF YOU SHOOT A FILM INSTEAD
-------------------------------------------------------------------

Name it hero.mp4 and put it in this folder. Same framing rules as above.

  10 to 15 seconds. It loops, so it should end roughly where it began or
  the jump shows.
  Landscape. H.264. 1920x1080 or 1280x720.
  Under about 8 MB -- every visitor downloads it.
  No sound needed; it plays muted, because no phone will autoplay a film
  with sound.

Until hero.mp4 exists the still is what shows, so nothing is broken by
not having one.
