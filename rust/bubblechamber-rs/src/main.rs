use nannou::color;
use nannou::prelude::*;
use ndarray::Array1;

use models::{Chamber, Particle};
use sim::cross_product;

mod gen;
mod models;
mod sim;

fn main() {
    nannou::app(model).update(update).simple_window(view).run();
}

struct Model {
    chamber: Chamber,
    particles: Vec<Particle>,
}

fn model(_app: &App) -> Model {
    Model {
        chamber: Chamber {
            magnetic_field: Array1::from_vec(vec![0., 0., 1.5]),
            friction: 0.2,
        },
        particles: gen::generate_particles(5, 6, 350.0),
    }
}

fn update(_app: &App, model: &mut Model, update: Update) {
    let tdelta = update.since_last.as_secs_f32();

    let mut to_split: Vec<usize> = Vec::with_capacity(model.particles.len());
    let mut to_remove: Vec<usize> = Vec::with_capacity(model.particles.len());

    for (i, p) in model.particles.iter_mut().enumerate() {
        // Last rites for dying particles, until their path is completely gone:
        if !p.is_alive {
            p.path.pop_front();
            if p.path.is_empty() {
                to_remove.push(i)
            }
            continue;
        }

        // Check if the particle decays:
        p.lifetime_s += tdelta;
        if p.lifetime_s >= p.decays_after {
            p.is_alive = false;
            if p.mass() > 1 {
                to_split.push(i);
            }
        }

        // Magnetic component of Lorentz force:
        let mag_force =
            p.charge() as f32 * cross_product(&p.velocity, &model.chamber.magnetic_field);
        // a = F / m
        let acceleration = mag_force / (p.mass() as f32);

        p.velocity += &(acceleration * tdelta);

        // Apply friction
        p.velocity *= 1.0 - (model.chamber.friction * tdelta);

        p.position += &(&p.velocity * tdelta);

        p.path
            .push_back([p.position[0], p.position[1], p.position[2]]);
    }

    for idx in to_split.drain(0..) {
        let mut new = gen::split_particle(&model.particles[idx]);
        model.particles.append(&mut new);
    }

    // Remove from highest to lowest index, so we don't go out of bounds.
    to_remove.sort_unstable_by(|a, b| b.cmp(a));
    for idx in to_remove.drain(0..) {
        model.particles.swap_remove(idx);
    }

    gen::maybe_add_particles(tdelta, &mut model.particles);
}

fn view(app: &App, model: &Model, frame: Frame) {
    let draw = app.draw();

    draw.background().color(WHITE);

    for p in model.particles.iter() {
        let path_len = p.path.len();
        let hue = (p.charge() as f32 / 20.0) + 0.5;

        draw.path()
            .stroke()
            .caps_round()
            .join_round()
            .weight(p.mass() as f32)
            .points_colored(p.path.iter().enumerate().map(|(i, pos)| {
                let pct_dist_to_head = i as f32 / path_len as f32;
                (
                    pt3(pos[0], pos[1], pos[2]),
                    color::hsva(hue, 0.66, pct_dist_to_head, pct_dist_to_head),
                )
            }));
    }

    // Write to the window frame.
    draw.to_frame(app, &frame).unwrap();
}
