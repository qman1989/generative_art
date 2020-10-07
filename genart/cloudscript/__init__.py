import datetime as dt
import logging

import cairo

from genart.fps import FPSCounter
from genart.util import parse_size

from .generator import generate_particles, make_superchamber
from .render import BubbleChamberRenderer
from .simulation import Simulation

log = logging.getLogger(__name__)


def register_parser(subparsers):
    parser = subparsers.add_parser(
        "cloudscript", help="A script made out of tiny bubble chambers."
    )

    parser.add_argument("-s", "--size", default="500x500")
    parser.add_argument("-m", "--magnet-stddev", type=float, default=2.0)
    parser.add_argument("-f", "--friction-lambda", type=float, default=2.0)
    parser.add_argument("-g", "--grid", action="store_true")

    parser.set_defaults(func=main)


def main(args, config):
    width, height = parse_size(args.size)

    ROWS = 10
    COLS = 10
    chamber = make_superchamber(
        width, height, ROWS, COLS, args.magnet_stddev, args.friction_lambda
    )
    particles = generate_particles(chamber)
    for i, row in enumerate(chamber.chambers):
        for j, col in enumerate(row):
            print(f"[{i}][{j}] {col} - {particles[i * ROWS + j]}")
    sim = Simulation(chamber, particles)

    out_file = config["output_dir"] / f"cloudscript_{dt.datetime.now().isoformat()}.svg"
    surface = cairo.SVGSurface(str(out_file), width, height)
    renderer = BubbleChamberRenderer(surface)

    if args.grid:
        renderer.add_grid(width, height, ROWS, COLS)

    fps = FPSCounter()

    sim.start()
    fps.start()
    while any(p.is_dirty for p in sim.particles):
        sim.step()
        renderer.render(sim)
        fps.frame_done()

    renderer.finalize(sim)
    surface.finish()
