THE FRONT PAGE PICTURE
======================

The hero is one picture running the full width of the screen with the
boutique's name and the WhatsApp button laid over it.

Three files control it, and none needs any code changed:

  hero-still.jpg        the wide picture. Laptops and tablets.
  hero-still-tall.jpg   the tall picture. Phones, under 640 pixels wide.
  hero.mp4              a film, if there ever is one. Plays over the still.

There are two pictures because a phone's hero is taller than it is wide and a
laptop's is more than twice as wide as it is tall. One file cannot serve both:
the wide one on a phone was covered from the middle out, so the phone saw
about a third of it.

Replace either file and that size of screen changes. Replace both and the
whole front page changes. That is the whole job.

If only hero-still.jpg is replaced, phones keep the tall one and nothing
breaks -- but the two will no longer match, so replace both together when you
can. If a file is missing altogether the page steps down on its own: no tall
file falls back to the wide one, no wide one falls back to a product
photograph. Nothing is ever left blank.


-------------------------------------------------------------------
SHOOTING THE PHOTOGRAPH
-------------------------------------------------------------------

A phone is fine. Portrait mode off, flash off, clean lens.

1. SHOOT IT TWICE -- SIDEWAYS, THEN UPRIGHT.
   Same setup, same light, same pose: turn the phone. The landscape one
   becomes hero-still.jpg, the upright one hero-still-tall.jpg. Everything
   below applies to both.

   If you only shoot one, shoot the upright one: most customers are on a
   phone.

2. LEAVE ROOM FOR THE WORDS.
   Sideways: the words sit over the lower LEFT. Put the model on the right
   and let the left be street, wall, cloth, sky -- anything quiet.
   Upright: the words run the full width across the lower half. Keep the
   model high and let the bottom half be skirt, fabric, floor -- nothing
   that matters. Her face must be in the top third.

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
THE FILES
-------------------------------------------------------------------

  The wide one          hero-still.jpg
                        landscape, at least 2000 px across, 2500 is better
  The tall one          hero-still-tall.jpg
                        upright, at least 1000 px across, 1400 is better
  Both, under about     600 KB each after saving, or the page loads slowly

Do not add a border, a frame or a cream margin. The picture must reach
all four edges -- the site puts its own darkening over the bottom so the
words stay readable, and a margin shows as a pale band down the sides.

WHAT IS ON THERE NOW, AND WHY IT IS TEMPORARY
---------------------------------------------

Nothing the boutique has sent is the right shape for a hero: every
photograph is one figure, upright, on a cream studio background. Cropped
to a wide band, they either lose the head or show cream down both sides.

So the pictures there now were built rather than shot. They are the
boutique's own catalogue photographs -- the black shirt dress, the pink
zari saree, the black sequin saree and the orange floral saree -- cut off
their backgrounds and stood together on a dark warm ground at different
sizes, so the eye reads them as a group. Four of them in the wide picture,
three in the tall one. Nothing about any garment was changed: no colour,
no shape, no work invented. It is an arrangement of real photographs.

  python3 build-hero.py            report only, writes nothing
  python3 build-hero.py --apply    rebuild both

Change which pieces appear, and where they stand, by editing LAYOUTS at the
top of build-hero.py. The two layouts are separate: the tall one carries only
three figures and lets them overlap, because side by side at that width each
would be a sliver. It refuses to write if a figure would land under the words,
above the line covering crops to, outside what a phone can see of the wide
file, or short of the bottom edge.

They are stand-ins and they are meant to be replaced. One real photograph
of the shop, shot to the rules above, will say more than four cut-outs on
a made-up background ever will -- and dropping the files in over these
needs no code changed at all.

framing-guide.png in this folder shows both shapes with the zones drawn
over the real page: where the model goes, where the words fall, and the
line the faces have to stay above.


-------------------------------------------------------------------
IF YOU SHOOT A FILM INSTEAD
-------------------------------------------------------------------

Name it hero.mp4 and put it in this folder. Same framing rules as above.
There is only one film -- it is used on every size -- so frame it the wide
way and accept that a phone sees the middle of it.

  10 to 15 seconds. It loops, so it should end roughly where it began or
  the jump shows.
  Landscape. H.264. 1920x1080 or 1280x720.
  Under about 8 MB -- every visitor downloads it.
  No sound needed; it plays muted, because no phone will autoplay a film
  with sound.

Until hero.mp4 exists the still is what shows, so nothing is broken by
not having one.
