import functools
from typing import Optional, Callable

from kivy.clock import ClockBase

from kv_classes import ComplexProgressBar
from utilities import schedule_interval


def inject_write_videofile(
        num_videos: int,
        total_allocated_percent: float,
        bar_total: Optional[ComplexProgressBar] = None,
        bar_current: Optional[ComplexProgressBar] = None
):
    event: Optional[ClockBase] = None
    total_v_start = 0

    def before():
        nonlocal event, total_v_start
        bar_current.reset()
        total_v_start = bar_total.value_normalized

        def up_bars(dt=None):
            bar_current.add(bar_current.max * 1.3 / 100)
            bar_total.add(bar_total.max * total_allocated_percent * (1.3 / num_videos) / 100)

        # increase the bars every sec, up to 1 min
        event = schedule_interval(up_bars, 1, 60)

    def after():
        nonlocal event
        event.cancel()
        bar_current.value_normalized = 1
        bar_total.value_normalized = total_v_start + total_allocated_percent / num_videos

    inject('3d-photo-inpainting.mesh', 'mesh.ImageSequenceClip', 'write_videofile',
           idempotent=True, before=before, after=after)


def exec_decorator(f: Callable, *, idempotent: bool = True, before: Optional[Callable] = None, after: Optional[Callable] = None):

    hash_val = (id(exec_decorator), id(before), id(after))

    if idempotent and getattr(f, '__IDEMPOTENT', False) == hash_val:
        return f

    @functools.wraps(f)
    def func(*args, **kwargs):
        if before is not None:
            before()
        out = f(*args, **kwargs)
        if after is not None:
            after()
        return out

    if idempotent:
        func.__IDEMPOTENT = hash_val

    return func


def inject(module_name: str, accessor: str, func_name: str, *, idempotent: bool = True,
           before: Optional[Callable] = None, after: Optional[Callable] = None):
    module = __import__(module_name)
    endpoint = module
    for chunk in accessor.split('.'):
        endpoint = endpoint.__dict__[chunk]
    func = getattr(endpoint, func_name)
    setattr(endpoint, func_name, exec_decorator(func, idempotent=idempotent, before=before, after=after))
    print(func, endpoint, module)
