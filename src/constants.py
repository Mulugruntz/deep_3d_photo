from pathlib import Path

CURRENT_DIR = Path('.').resolve()
DIR_3D_PI = CURRENT_DIR / '3d-photo-inpainting'
CONFIG_ORIGIN = DIR_3D_PI / 'argument.yml'
CONFIG_CUSTOM = CURRENT_DIR / 'custom-conf.yml'
MODELS_DIR = CURRENT_DIR / 'models'
MODELS_URL_ROOT = 'https://filebox.ece.vt.edu/~jbhuang/project/3DPhoto/model'
MODELS = {
    'depth_edge_model_ckpt': 'edge-model.pth',
    'depth_feat_model_ckpt': 'depth-model.pth',
    'rgb_feat_model_ckpt': 'color-model.pth',
    'MiDaS_model_ckpt': 'model.pt',
}
