PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
xcrun -sdk macosx metal -c "$PROJECT_ROOT/src/add.metal" -o "$PROJECT_ROOT/src/MyLibrary.air"
xcrun -sdk macosx metallib "$PROJECT_ROOT/src/MyLibrary.air" -o "$PROJECT_ROOT/src/default.metallib"
python3 -m build
python3 -m pip install --break-system-packages --force-reinstall "$PROJECT_ROOT/dist/mymodule-0.1-cp313-cp313-macosx_14_0_arm64.whl"
