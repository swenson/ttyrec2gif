from __future__ import print_function, unicode_literals
from PIL import Image

import pyte
import struct
from images2gif import writeGif
import numpy as np


screen_width = 130
screen_height = 24

stream = pyte.Stream()
screen = pyte.Screen(screen_width, screen_height)
stream.attach(screen)
stream.feed("Hello")


def frames(fname):
  script = open(fname).read()
  offset = 0
  while offset < len(script):
    (delay, delayus, length) = struct.unpack('<III', script[offset:offset+12])
    offset += 12
    frame = script[offset:offset+length].decode('cp437')
    yield frame
    offset += length



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

# for row in letters[178]:
#   print(''.join(str(x / 168) for x in row))


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
  img = Image.new('RGB', (screen_width * char_width, screen_height * char_height))

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
          img.putpixel((x, y), color)
  img.save("%d.png" % num)
  print(num)

for i, frame in enumerate(frames('/Users/swenson/nh-ttyrec/2010-02-03.05-59-29.ttyrec')):
  stream.feed(frame)
  render(i)

