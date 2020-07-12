from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import numpy as np
import os

import vispy
from imageio.core import Array
from kivy.clock import Clock, mainthread
from tqdm import tqdm
import yaml

from constants import CONFIG_ORIGIN, CONFIG_CUSTOM, MODELS_DIR, MODELS
from injector import inject_write_videofile
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from kv_classes import FileChoose
from kv_classes.complex_progress_bar import ComplexProgressBar
from mesh import write_ply, read_ply, output_3d_photo
from utilities import schedule_interval, check_models_existence, f
from utils import get_MiDaS_samples, read_MiDaS_depth
import torch
import cv2
import imageio
import copy
from networks import Inpaint_Color_Net, Inpaint_Depth_Net, Inpaint_Edge_Net
from MiDaS.run import run_depth
from MiDaS.monodepth_net import MonoDepthNet
import MiDaS.MiDaS_utils as MiDaS_utils
from bilateral_filtering import sparse_bilateral_filtering
from kv_classes.localization import _


def init_fs(config):
    os.makedirs(config['mesh_folder'], exist_ok=True)
    os.makedirs(config['video_folder'], exist_ok=True)
    os.makedirs(config['depth_folder'], exist_ok=True)


def wrap_3d_pi_with_override(image_filename: Path, *,
                             depth_handler: Optional[FileChoose] = None,
                             bar_total: Optional[ComplexProgressBar] = None,
                             bar_current: Optional[ComplexProgressBar] = None,
                             just_depth: bool = False,
                             ):
    # with the GUI we always have exactly 1 input image file
    number_input_image = 1
    bar_total.reset()
    bar_current.reset()
    real_image_filename = image_filename.resolve()
    if not real_image_filename.is_file():
        raise ValueError(f(_('File {real_image_filename} does not exist!')))

    chunk, ext = os.path.splitext(real_image_filename)
    dirname, filename = os.path.split(chunk)
    origin_conf = CONFIG_CUSTOM if CONFIG_CUSTOM.is_file() else CONFIG_ORIGIN
    with open(origin_conf, 'r') as config_file:
        config = yaml.load(config_file)

    config['depth_folder'] = str(Path(config['depth_folder']).resolve())
    config['mesh_folder'] = str(Path(config['mesh_folder']).resolve())
    config['video_folder'] = str(Path(config['video_folder']).resolve())
    config['src_folder'] = dirname
    config['specific'] = filename
    config['img_format'] = ext
    for name, filename in MODELS.items():
        config[name] = str(MODELS_DIR / filename)

    missing_models = check_models_existence()

    with open(CONFIG_CUSTOM, 'w') as config_file:
        yaml.dump(config, config_file, default_flow_style=None)

    if not just_depth:
        from_file = Path(depth_handler.bnd_image.source).resolve()
        to_file = Path(config['depth_folder'], from_file.parts[-1].rsplit('.', maxsplit=1)[0] + '.png')

        if from_file.samefile(to_file):
            print(f(_('Depth file {from_file} is already in the correct location. No copy needed.')))
        else:
            print(f(_('Copying Depth file from {from_file} to {to_file}')))
            shutil.copy(str(from_file), str(to_file))
            update_image_handler(image_handler=depth_handler, path=to_file)

        inject_write_videofile(
            num_videos=len(config['video_postfix']) * number_input_image,
            total_allocated_percent=20 / 100,
            bar_total=bar_total,
            bar_current=bar_current,
        )

    if not missing_models:
        bar_current.add(bar_current.max)
        bar_total.add(bar_total.max * 2 / 100)
        wrap_3d_photo_inpainting(
            CONFIG_CUSTOM,
            depth_handler=depth_handler,
            bar_total=bar_total,
            bar_current=bar_current,
            just_depth=just_depth
        )
    else:
        raise ValueError(_("Models have not been downloaded!"))


def wrap_3d_photo_inpainting(config_path, *,
                             depth_handler: Optional[FileChoose] = None,
                             bar_total: Optional[ComplexProgressBar] = None,
                             bar_current: Optional[ComplexProgressBar] = None,
                             just_depth: bool = False
                             ):
    bar_current.reset()
    config = yaml.load(open(config_path, 'r'))
    if config['offscreen_rendering'] is True:
        vispy.use(app='egl')
    init_fs(config)
    sample_list = get_MiDaS_samples(config['src_folder'], config['depth_folder'], config, config['specific'])
    normal_canvas, all_canvas = None, None

    if isinstance(config["gpu_ids"], int) and (config["gpu_ids"] >= 0):
        device = config["gpu_ids"]
    else:
        device = "cpu"

    bar_current.add(bar_current.max)
    bar_total.add(bar_total.max * 2 / 100)

    print(f(_("running on device {device}")))

    for idx in tqdm(range(len(sample_list))):
        bar_current.reset()
        depth = None
        sample = sample_list[idx]
        print(f(_("Current Source ==> {sample['src_pair_name']}")))
        mesh_fi = os.path.join(config['mesh_folder'], sample['src_pair_name'] +'.ply')
        image = imageio.imread(sample['ref_img_fi'])

        print(f(_("Running depth extraction at {datetime.now():%Y-%m-%d %H:%M:%S.%f}")))
        if just_depth or config['require_midas'] is True:
            run_depth([sample['ref_img_fi']], config['src_folder'], config['depth_folder'],
                      config['MiDaS_model_ckpt'], MonoDepthNet, MiDaS_utils, target_w=640)

            update_image_handler(image_handler=depth_handler,
                                 path=Path(f"{config['depth_folder']}/{sample['src_pair_name']}.png"))

        if just_depth:
            bar_total.reset()
            bar_total.value = bar_total.max
            bar_current.reset()
            bar_current.value = bar_current.max
            return

        bar_current.add(bar_current.max)
        bar_total.add(bar_total.max * (2 / len(sample_list)) / 100)

        bar_current.reset()

        image = prepare_config_and_image(config=config, sample=sample, image=image)

        bar_current.add(bar_current.max)
        bar_total.add(bar_total.max * (2 / len(sample_list)) / 100)

        bar_current.reset()

        image = cv2.resize(image, (config['output_w'], config['output_h']), interpolation=cv2.INTER_AREA)
        depth = read_MiDaS_depth(sample['depth_fi'], 3.0, config['output_h'], config['output_w'])
        mean_loc_depth = depth[depth.shape[0]//2, depth.shape[1]//2]

        bar_current.add(bar_current.max)
        bar_total.add(bar_total.max * (2 / len(sample_list)) / 100)

        bar_current.reset()

        if not(config['load_ply'] is True and os.path.exists(mesh_fi)):
            vis_photos, vis_depths = sparse_bilateral_filtering(depth.copy(), image.copy(), config, num_iter=config['sparse_iter'], spdb=False)
            depth = vis_depths[-1]
            model = None
            torch.cuda.empty_cache()
            print(_("Start Running 3D_Photo ..."))

            depth_edge_model = load_edge_model(device=device, depth_edge_model_ckpt=config['depth_edge_model_ckpt'])
            depth_edge_model.eval()

            depth_feat_model = load_depth_model(device=device, depth_feat_model_ckpt=config['depth_feat_model_ckpt'])

            rgb_model = load_rgb_model(device=device, rgb_feat_model_ckpt=config['rgb_feat_model_ckpt'])
            graph = None

            def up_bars(dt=None):
                bar_current.add(bar_current.max * 1.5 / 100)
                bar_total.add(bar_total.max * (1 / len(sample_list)) / 100)

            # increase the bars every 5 sec, up to 5 min
            event = schedule_interval(up_bars, 5, 60 * 5)

            print(f(_("Writing depth ply (and basically doing everything) at {datetime.now():%Y-%m-%d %H:%M:%S.%f}")))
            rt_info = write_ply(image,
                                  depth,
                                  sample['int_mtx'],
                                  mesh_fi,
                                  config,
                                  rgb_model,
                                  depth_edge_model,
                                  depth_edge_model,
                                  depth_feat_model)

            if rt_info is False:
                continue
            rgb_model = None
            color_feat_model = None
            depth_edge_model = None
            depth_feat_model = None
            torch.cuda.empty_cache()

            event.cancel()

        bar_current.add(bar_current.max)
        bar_total.value_normalized = 75 / 100

        bar_current.reset()

        props = read_ply(mesh_fi) if config['save_ply'] is True or config['load_ply'] is True else rt_info
        make_video(
            sample=sample, config=config, props=props,
            depth=depth, normal_canvas=normal_canvas, all_canvas=all_canvas,
        )

        bar_current.value_normalized = 1
        bar_total.value_normalized = 1


@mainthread
def update_image_handler(*, image_handler: FileChoose, path: Path):
    path = path.resolve()
    image_handler.bnd_image.set_source(path)
    image_handler.bnd_text_input.text = str(path)


def prepare_config_and_image(config: Dict, sample: Dict, image: Array) -> Array:
    if 'npy' in config['depth_format']:
        config['output_h'], config['output_w'] = np.load(sample['depth_fi']).shape[:2]
    else:
        config['output_h'], config['output_w'] = imageio.imread(sample['depth_fi']).shape[:2]
    frac = config['longer_side_len'] / max(config['output_h'], config['output_w'])
    config['output_h'], config['output_w'] = int(config['output_h'] * frac), int(config['output_w'] * frac)
    config['original_h'], config['original_w'] = config['output_h'], config['output_w']
    if image.ndim == 2:
        image = image[..., None].repeat(3, -1)
    if np.sum(np.abs(image[..., 0] - image[..., 1])) == 0 and np.sum(np.abs(image[..., 1] - image[..., 2])) == 0:
        config['gray_image'] = True
    else:
        config['gray_image'] = False
    return image


def load_edge_model(device: str, depth_edge_model_ckpt: str) -> Inpaint_Edge_Net:
    print(f(_("Loading edge model at {datetime.now():%Y-%m-%d %H:%M:%S.%f}")))
    depth_edge_model = Inpaint_Edge_Net(init_weights=True)
    depth_edge_weight = torch.load(depth_edge_model_ckpt, map_location=torch.device(device))
    depth_edge_model.load_state_dict(depth_edge_weight)
    return depth_edge_model.to(device)


def load_depth_model(device: str, depth_feat_model_ckpt: str) -> Inpaint_Depth_Net:
    print(f(_("Loading depth model at {datetime.now():%Y-%m-%d %H:%M:%S.%f}")))
    depth_feat_model = Inpaint_Depth_Net()
    depth_feat_weight = torch.load(depth_feat_model_ckpt, map_location=torch.device(device))
    depth_feat_model.load_state_dict(depth_feat_weight, strict=True)
    depth_feat_model = depth_feat_model.to(device)
    depth_feat_model.eval()
    return depth_feat_model.to(device)


def load_rgb_model(device: str, rgb_feat_model_ckpt: str) -> Inpaint_Color_Net:
    print(f(_("Loading rgb model at {datetime.now():%Y-%m-%d %H:%M:%S.%f}")))
    rgb_model = Inpaint_Color_Net()
    rgb_feat_weight = torch.load(rgb_feat_model_ckpt, map_location=torch.device(device))
    rgb_model.load_state_dict(rgb_feat_weight)
    rgb_model.eval()
    return rgb_model.to(device)


def make_video(sample, config, props, depth, normal_canvas, all_canvas):
    image = imageio.imread(sample['ref_img_fi'])

    mean_loc_depth = depth[depth.shape[0] // 2, depth.shape[1] // 2]

    verts, colors, faces, Height, Width, hFov, vFov = props

    print(f(_("Making video at {datetime.now():%Y-%m-%d %H:%M:%S.%f}")))
    videos_poses, video_basename = copy.deepcopy(sample['tgts_poses']), sample['tgt_name']
    top = (config.get('original_h') // 2 - sample['int_mtx'][1, 2] * config['output_h'])
    left = (config.get('original_w') // 2 - sample['int_mtx'][0, 2] * config['output_w'])
    down, right = top + config['output_h'], left + config['output_w']
    border = [int(xx) for xx in [top, down, left, right]]
    normal_canvas, all_canvas = output_3d_photo(verts.copy(), colors.copy(), faces.copy(), copy.deepcopy(Height),
                                                copy.deepcopy(Width), copy.deepcopy(hFov), copy.deepcopy(vFov),
                                                copy.deepcopy(sample['tgt_pose']), sample['video_postfix'],
                                                copy.deepcopy(sample['ref_pose']),
                                                copy.deepcopy(config['video_folder']),
                                                image.copy(), copy.deepcopy(sample['int_mtx']), config, image,
                                                videos_poses, video_basename, config.get('original_h'),
                                                config.get('original_w'), border=border, depth=depth,
                                                normal_canvas=normal_canvas, all_canvas=all_canvas,
                                                mean_loc_depth=mean_loc_depth)

    print(f(_("{len(sample['video_postfix'])} videos done in {Path(config['video_folder']).resolve()}")))


if __name__ == '__main__':
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--config', type=str, default='argument.yml', help='Configure of post processing')
    # args = parser.parse_args()
    # wrap_3d_photo_inpainting(config_path=args.config)
    wrap_3d_pi_with_override(Path('.', '3d-photo-inpainting', 'image', 'Ksyu and hat.jpeg'))
