"""
some simple utility functions for working with colors
"""
from colorsys import hsv_to_rgb, rgb_to_hsv
import webcolors

default_hsv = dict(
    h= 0.5,
    s = 0.8,
    v = 0.8
)


def is_valid_rgb(r, g, b):
    """
    check that an rgb color is valid
    :params r,g,b: (0,1) range floats
    :return: True if valid, otherwise False
    """
    return all([0 <= x <= 1 for x in (r, g, b)])


def is_valid_RGB(r, g, b):
    """
    check that an RGB color is valid
    :params r,g,b: (0,255) range floats
    :return: True if valid, otherwise False
    """
    return all([0 <= x <= 255 for x in (r, g, b)])


def rgb_to_RGB(r, g, b):
    """
    Convert rgb values to RGB values
    :param r,g,b: (0,1) range floats
    :return: a 3 element tuple of RGB values in the range (0, 255)
    """
    return (int(r * 255), int(g * 255), int(b * 255))


def RGB_to_rgb(r, g, b):
    """
    Convert RGB values to rgb values
    :param r,g,b: (0,255) range floats
    :return: a 3 element tuple of rgb values in the range (0, 1)
    """
    return (float(r) / 255, float(g) / 255, float(b) / 255)


def rgb_to_hex(r, g, b):
    """
    Generate a html hex color string from r,g,b values
    
    :params r,g,b: (0,1) range floats
    :return: a html compatible hex color string
    """
    assert is_valid_rgb(r, g, b), "Error, r,g,b must be (0,1) range floats"
    R,G,B = rgb_to_RGB(r,g,b)
    return "#{:02x}{:02x}{:02x}".format(R, G, B)


def gen_color(h, s=default_hsv["s"], v=default_hsv["v"]):
    """
    generate rgb colors using golden-ratio
    adapted from https://www.continuum.io/blog/developer-blog/drawing-brain-bokeh
    :param h: base value for hue
    :param s: saturation
    :param v: value (brightness)
    :return: a html compatible hex color string
    """
    golden_ratio = (1 + 5 ** 0.5) / 2
    h += golden_ratio
    h %= 1
    return rgb_to_hex(*hsv_to_rgb(h, s, v))


def desaturate_rgb(rgb, amount):
    """
    reduce the saturation of an rgb color
    
    :param rgb: a 3-element tuple containing r,g,b values (as (0,1) floats)
    :param amount: factor to scale the saturation by
    :return: a html compatible hex color string
    """
    assert is_valid_rgb(*rgb), "Error, r,g,b must be (0,1) range floats"
    hsv = rgb_to_hsv(*rgb)
    desat_hsv = (hsv[0], hsv[1] * amount, hsv[2])
    desat_rgb = hsv_to_rgb(*desat_hsv)
    return rgb_to_hex(*desat_rgb)


def desaturate_hex(color, amount):
    return desaturate_rgb(RGB_to_rgb(*webcolors.hex_to_rgb(color)), amount)


def desaturate_named_color(name, amount):
    return desaturate_rgb(RGB_to_rgb(*webcolors.name_to_rgb(name)), amount)
