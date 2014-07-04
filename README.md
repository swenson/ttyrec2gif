# ttyrec2gif

Call with a single argument, the ttyrec to convert.

This program directly emulates the VT100 screen in Python and converts
to a GIF in-memory.
This is significantly faster than the screenshotting methods.

You'll need the Python packages `pyte`, `Pillow`, and `numpy` installed to run it.
I'd recommend setting up a `virtualenv` for this:

```sh
virtualenv venv
source venv/bin/activate
pip install numpy pyte Pillow
```

Now, find a ttyrec you want.
Example: download a fun NetHack ttyrec for an ascension from
http://nethack.wikia.com/wiki/Notable_ascensions (you may need to `bunzip2` it).

Then run

```sh
virtualenv
./ttyrec

Outputs out00000.gif, out00001.gif, etc., that are
roughly 5 minutes long.

If you want a full GIF, just run:

```sh
convert out*.gif combined.gif
```

Or, to do the same thing with optimization (which will probably
be very, very slow):

```sh
convert out*.gif -layers Optimize combined.gif
```
