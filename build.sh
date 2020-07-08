pushd /Users/sgiffard/PycharmProjects/deep_3d_photo/Deep3DPhotoApp
pipenv run python -m PyInstaller -y --clean --windowed --name Deep3DPhoto \
    --exclude-module enchant  --exclude-module twisted --exclude-module _tkinter --exclude-module Tkinter \
    --hidden-import=pkg_resources.py2_warn \
    --paths=src \
    --paths=3d-photo-inpainting \
    ../main.py
pipenv run python -m PyInstaller -y --clean --windowed Deep3DPhoto.spec
/Users/sgiffard/PycharmProjects/deep_3d_photo/Deep3DPhotoApp/dist/Deep3DPhoto.app/Contents/MacOS/Deep3DPhoto
popd