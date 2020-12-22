from math import pi, tau
from typing import Sequence

import cairo
from numpy.random import Generator

from genart.cairoctx import rotation, translation
from genart.geom import points_along_arc
from genart.numbering import int_to_roman


def _calendar_base(
    ctx: cairo.Context,
    pos_x: float,
    pos_y: float,
    radius_outer: float,
    radius_inner: float,
    chunks: int,
):
    ctx.arc(pos_x, pos_y, radius_outer, 0, tau)
    ctx.stroke_preserve()

    ctx.arc(pos_x, pos_y, radius_inner, 0, tau)
    ctx.stroke()

    for (start_x, start_y), (end_x, end_y) in zip(
        points_along_arc(pos_x, pos_y, radius_inner, 0, tau, chunks),
        points_along_arc(pos_x, pos_y, radius_outer, 0, tau, chunks),
    ):
        ctx.move_to(start_x, start_y)
        ctx.line_to(end_x, end_y)
        ctx.stroke()


def draw_circular_roman(
    ctx: cairo.Context,
    rng: Generator,
    pos_x: float,
    pos_y: float,
    radius_outer: float,
    radius_inner: float,
):
    chunks = rng.integers(6, 16)
    _calendar_base(ctx, pos_x, pos_y, radius_outer, radius_inner, chunks)

    ctx.select_font_face("Times", cairo.FontSlant.NORMAL, cairo.FontWeight.BOLD)
    font_size = 0.8 * (radius_outer - radius_inner)
    ctx.set_font_size(font_size)

    angle_offset = pi / chunks
    for i, (x, y) in enumerate(
        points_along_arc(
            pos_x,
            pos_y,
            (radius_inner + radius_outer) / 2.0,
            angle_offset,
            angle_offset + tau,
            chunks,
        ),
        1,
    ):
        with translation(ctx, x, y), rotation(
            ctx, (i * tau / chunks) + (pi / 2) - angle_offset
        ):
            roman = int_to_roman(i)
            extents = ctx.text_extents(roman)

            ctx.move_to(-1 * extents.width / 2.0, extents.height / 2.0)
            ctx.show_text(roman)
            ctx.new_path()


def _calendar_mapped(
    ctx: cairo.Context,
    rng: Generator,
    pos_x: float,
    pos_y: float,
    radius_outer: float,
    radius_inner: float,
    mapping: Sequence[str],
):
    chunks = rng.integers(6, len(mapping))
    _calendar_base(ctx, pos_x, pos_y, radius_outer, radius_inner, chunks)

    ctx.select_font_face("Menlo", cairo.FontSlant.NORMAL, cairo.FontWeight.BOLD)
    font_size = 0.8 * (radius_outer - radius_inner)
    ctx.set_font_size(font_size)

    angle_offset = pi / chunks
    for i, (x, y) in enumerate(
        points_along_arc(
            pos_x,
            pos_y,
            (radius_inner + radius_outer) / 2.0,
            angle_offset,
            angle_offset + tau,
            chunks,
        ),
        1,
    ):
        with translation(ctx, x, y), rotation(
            ctx, (i * tau / chunks) + (pi / 2) - angle_offset
        ):
            symbol = mapping[i]
            # Weird unicode behavior workaround:
            if len(symbol) == 2:
                symbol = symbol[0]
            extents = ctx.text_extents(symbol)

            ctx.move_to(-1 * extents.width / 2.0, extents.height / 2.0)
            ctx.show_text(symbol)
            ctx.new_path()


def draw_circular_astrological_planets(
    ctx: cairo.Context,
    rng: Generator,
    pos_x: float,
    pos_y: float,
    radius_outer: float,
    radius_inner: float,
):
    UNICODE_ASTROLOGICAL_PLANETS = (
        "☉",
        "☽",
        "☿",
        "♀",
        "⊕",
        "♁",
        "♂",
        "♃",
        "♄",
        "♅",
        "⛢",
        "♆",
        "♇",
    )
    _calendar_mapped(
        ctx, rng, pos_x, pos_y, radius_outer, radius_inner, UNICODE_ASTROLOGICAL_PLANETS
    )


def draw_circular_zodiac(
    ctx: cairo.Context,
    rng: Generator,
    pos_x: float,
    pos_y: float,
    radius_outer: float,
    radius_inner: float,
):
    UNICODE_ZODIAC_SIGNS = (
        "♈︎",
        "♉︎",
        "♊︎",
        "♋︎",
        "♌︎",
        "♍︎",
        "♎︎",
        "♏︎",
        "♐︎",
        "♑︎",
        "♒︎",
        "♓︎",
    )
    _calendar_mapped(
        ctx, rng, pos_x, pos_y, radius_outer, radius_inner, UNICODE_ZODIAC_SIGNS
    )
