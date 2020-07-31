from __future__ import annotations
import os
from pathlib import Path
from typing import List, Optional, Callable
from inspect import currentframe

import requests
from kivy.clock import Clock

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from kv_classes import ComplexProgressBar
from constants import MODELS_DIR, MODELS_URL_ROOT, MODELS


from kv_classes.localization import _


def f(s):
    frame = currentframe().f_back
    return eval(f"""f'''{s}'''""", frame.f_globals, frame.f_locals)


def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return f"{num:3.1f} {unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f} Yi{suffix}"


def download_models(models: List, *,
                    bar_total: Optional[ComplexProgressBar] = None,
                    bar_current: Optional[ComplexProgressBar] = None):
    os.makedirs(MODELS_DIR, exist_ok=True)

    to_download = []
    for model in models:
        if model not in MODELS:
            raise ValueError(f(_("Unknown model {model}!")))
        remote_url = f'{MODELS_URL_ROOT}/{MODELS[model]}'
        local_path = MODELS_DIR / MODELS[model]
        to_download.append((remote_url, local_path))

    if bar_total is not None:
        size = get_total_size([i[0] for i in to_download])
        bar_total.max = size
        bar_total.text = lambda *, internal_name, max_: f"{internal_name} 0 / {sizeof_fmt(max_)}"

    for remote_url, local_path in to_download:
        download_file(remote_url, local_path, bar_total=bar_total, bar_current=bar_current)


def get_total_size(urls: List) -> int:
    size = 0
    for url in urls:
        with requests.get(url, stream=True) as r:
            size += int(r.headers.get('Content-Length', 0))
    return size


def download_file(remote_url, local_path: Path, *,
                  n_chunk=1,
                  bar_total: Optional[ComplexProgressBar] = None,
                  bar_current: Optional[ComplexProgressBar] = None):
    with requests.get(remote_url, stream=True) as r:
        # Estimates the number of bar updates
        block_size = 1024
        file_size = int(r.headers.get('Content-Length', 0))
        filename = local_path.name
        if bar_current is not None:
            bar_current.reset()
            bar_current.max = file_size
            bar_current.text = lambda *, internal_name, max_: f"{internal_name}: {filename} \n 0 / {sizeof_fmt(max_)}"

        current_placeholder = lambda *, internal_name, max_, value: (
            f"{internal_name}:\n"
            f"{filename}\n"
            f"{sizeof_fmt(value)} / {max_}"
        )
        total_placeholder = lambda *, internal_name, max_, value: (
            f"{internal_name}\n"
            f"{sizeof_fmt(value)} / {max_}"
        )

        with open(local_path, 'wb') as f:
            for i, chunk in enumerate(r.iter_content(chunk_size=n_chunk * block_size)):
                f.write(chunk)

                if bar_current is not None:
                    bar_current.add(n_chunk * block_size)
                    bar_current.text = current_placeholder

                if bar_total is not None:
                    bar_total.add(n_chunk * block_size)
                    bar_total.text = total_placeholder


def schedule_interval(func: Callable, interval: float, until: float):
    event = Clock.schedule_interval(func, interval)
    Clock.schedule_once(lambda dt: Clock.unschedule(event), until)
    return event


def check_models_existence() -> List:
    """
    depth_edge_model_ckpt: checkpoints/edge-model.pth
    depth_feat_model_ckpt: checkpoints/depth-model.pth
    rgb_feat_model_ckpt: checkpoints/color-model.pth
    MiDaS_model_ckpt: MiDaS/model.pt
    """
    missing = []
    for name, filename in MODELS.items():
        if not (MODELS_DIR / filename).is_file():
            missing.append(name)
            continue
        remote_size = get_total_size([f'{MODELS_URL_ROOT}/{MODELS[name]}'])
        local_size = (MODELS_DIR / filename).lstat().st_size
        if remote_size != local_size:
            missing.append(name)
            print(f(_('File {MODELS[name]} is incorrect (remote: {remote_size} != local: {local_size}). Will re-download.')))

    if missing:
        print(f(_('The following models are missing: {", ".join(MODELS[m] for m in missing)}! Please download them first.')))
        print(_('You can find them there:'))
        print(*[f'{MODELS_URL_ROOT}/{MODELS[m]}' for m in missing], sep='\n')
        print(f(_('Please put them in {MODELS_DIR}')))

    return missing
