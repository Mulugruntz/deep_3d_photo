from pathlib import Path

MAIN_DIR = Path(__file__).parent.parent.resolve()
ROOT_INSTALL_DIR = MAIN_DIR.parent
RESOURCE_DIR = MAIN_DIR / 'res'
DIR_3D_PI = MAIN_DIR / '3d-photo-inpainting'
CONFIG_ORIGIN = DIR_3D_PI / 'argument.yml'
CONFIG_CUSTOM = MAIN_DIR / 'custom-conf.yml'
LOCALE_DIR = MAIN_DIR / 'locale'
MODELS_DIR = MAIN_DIR / 'models'
MODELS_URL_ROOT = 'https://filebox.ece.vt.edu/~jbhuang/project/3DPhoto/model'
MODELS = {
    'depth_edge_model_ckpt': 'edge-model.pth',
    'depth_feat_model_ckpt': 'depth-model.pth',
    'rgb_feat_model_ckpt': 'color-model.pth',
    'MiDaS_model_ckpt': 'model.pt',
}
BLANK_IMAGE = RESOURCE_DIR / 'blank-transparent.png'
