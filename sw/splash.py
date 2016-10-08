import sys
import t3

def args(*a):
    return a

def anim_starter(func, anims):
    for i, args in enumerate(anims):
        if args is not None:
            t3.start_task(func(*args))
            yield 1/10


def bluish():
    hue = t3.random_uniform(0.43, 0.67)
    sat = 0.26
    lightness = 0.4
    return t3.hls_to_rgb(hue, sat, lightness)


def reddish():
    hue = t3.random_uniform(-0.07, 0.07)
    sat = 0.26
    lightness = 0.4
    return t3.hls_to_rgb(hue, sat, lightness)

def splash():
    t3.start_task(anim_starter(t3.display.anim_pixel, (
        args((1, 0), *bluish()),
        args((0, 0), *bluish()),
        args((2, 0), *bluish()),
        args((1, 1), *bluish()),
        args((1, 2), *bluish()),
    )))

    yield 0.7

    t3.start_task(anim_starter(t3.display.anim_pixel, (
        (2, 0, 0, 0),
        (0, 0, 0, 0),
        (1, 0, 0, 0),
        None,
        (7, 0, 0, 0),
    )))

    yield 0.3

    t3.start_task(anim_starter(t3.display.anim_pixel, (
        args(8, *reddish()),
        args(0, *reddish()),
        None,
        None,
        args(4, *reddish()),
    )))

    yield 0.7

    t3.start_task(anim_starter(t3.display.anim_pixel, (
        (8, 0, 0, 0),
        (0, 0, 0, 0),
        None,
        None,
        (4, 0, 0, 0, 25),
    )))

    yield 1

    import launcher
    t3.start_task(launcher.main_menu())
