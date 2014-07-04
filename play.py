# Call with a single argument, the ttyrec to convert
#
# Outputs out00000.gif, out00001.gif, etc., that are
# roughly 5 minutes long.
#
# If you want a full GIF, just run:
#   convert out*.gif combined.gif
#
# Or, to do the same thing with optimization (which will probably
# be very, very slow):
#   convert out*.gif -layers Optimize combined.gif


from __future__ import print_function, unicode_literals

from images2gif import writeGif
from PIL import Image
from threading import Thread
import numpy as np
import os
import pyte
import struct
import sys
import time

optimize_gifs = False # requires 'convert' program from ImageMagick
screen_width = 130
screen_height = 24
speedup = 5.0 # make it go faster than normal

stream = pyte.Stream()
screen = pyte.Screen(screen_width, screen_height)
stream.attach(screen)


def frames(fname):
  script = open(fname).read()
  offset = 0
  (delay, delayus, length) = struct.unpack('<III', script[offset:offset+12])
  last_delay = delay + delayus / 1000000.0
  while offset < len(script):
    (delay, delayus, length) = struct.unpack('<III', script[offset:offset+12])
    offset += 12
    frame = script[offset:offset+length].decode('cp437')
    delay = delay + delayus / 1000000.0
    delay, last_delay = delay - last_delay, delay
    yield frame, delay
    offset += length



# read in the Codepage-437 and convert it to 9x16 VGA glyphs
# This image is in the public domain.
font = Image.open('Codepage-437.png')
font.convert('RGB')

letters = []


char_width = 9
char_height = 16
width = 304
height = 144
chars_per_row = 32
x_offset = 8
y_offset = 8

for char in xrange(256):
  y_start = y_offset + char / chars_per_row * char_height
  x_start = x_offset + char % chars_per_row * char_width
  value = []
  for y in xrange(y_start, y_start + char_height):
    row = []
    for x in xrange(x_start, x_start + char_width):
      v = font.getpixel((x, y))
      row.append(v)
    value.append(row)
  letters.append(value)

# classic VGA colors
colors = {}
colors['black'] = (0,0,0)
colors['red'] = (170,0,0)
colors['green'] = (0, 170, 0)
colors['brown'] = (170, 85, 0)
colors['yellow'] = colors['brown']
colors['blue'] = (0,0,170)
colors['magenta'] = (170,0,170)
colors['cyan'] = (0,170,170)
colors['gray'] = (170,170,170)
colors['white'] = (255,255,255)

colors['black_bold'] = (85,85,85)
colors['red_bold'] = (255,85,85)
colors['green_bold'] = (85, 255, 85)
colors['brown_bold'] = (255, 255, 85)
colors['yellow_bold'] = colors['brown_bold']
colors['blue_bold'] = (85,85,255)
colors['magenta_bold'] = (255,85,255)
colors['cyan_bold'] = (85,255,255)
colors['gray_bold'] = (255,255,255)
colors['white_bold'] = (255,255,255)


def render(num):
  img = np.zeros((screen_height * char_height, screen_width * char_width, 3), np.uint8)
  for yc, line in enumerate(screen.buffer):
    for xc, ch in enumerate(line):
      try:
        char = ch.data.encode('cp437')
      except:
        char = ' '
      if ord(char) == 32:
        continue
      fg = ch.fg
      bg = ch.bg
      bold = ch.bold

      values = letters[ord(char)]
      for yy, row in enumerate(values):
        for xx, v in enumerate(row):
          if v == 0 and (bg == 'default' or bg == 'black'):
            continue
          if v == 0:
            c = bg if bg != 'default' else 'black'
          else:
            c = fg if fg != 'default' else 'gray'
          if bold:
            c += '_bold'
          color = colors[c]
          y = yc * char_height + yy
          x = xc * char_width + xx
          img[y,x,:] = color
  return img

images = []
delays = []
play_time = 0.0
running_time = 0.0
frame_start = time.time()
output = 0

def writeOut(fname, images, delays):
  print("Writing %s" % fname)
  start = time.time()
  writeGif('temp' + fname, images, duration=delays, subRectangles=False)

  if optimize_gifs:
    os.system('convert temp%s -layers Optimize %s' % (fname, fname))
  else:
    os.system('cp temp%s %s' % (fname, fname))

  os.system('rm temp%s' % fname)
  print("Done writing %s after %.3f seconds" % (fname, time.time() - start))

for i, (frame, delay) in enumerate(frames(sys.argv[1])):
  stream.feed(frame)
  images.append(render(i))
  if delay > 2.0:
    delay = 2.0 # don't wait too long
  delays.append(delay / speedup)
  play_time += delay
  running_time += delay / speedup
  print("%5d  delay %3.3f  running %.2f" % (i, delay, running_time))
  if running_time > 5 * 60.0:
    writeOut('out%05d.gif' % output, images, delays)
    output += 1
    images = []
    delays = []
    running_time = 0.0
frame_end = time.time()

if images:
  writeOut('out%05d.gif' % output, images, delays)

print("Game time: %.3f seconds" % play_time)
print("Frame rendering time: %.3f seconds, %.3f ms per frame" % (frame_end - frame_start, 1000.0 * (frame_end - frame_start) / float(i)))
