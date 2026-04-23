import sys
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext as build_ext_orig
import pybind11

class build_ext(build_ext_orig):
    def build_extensions(self):
        self.compiler.src_extensions.append('.mm')
        self.compiler.set_executable('compiler_so', '/opt/homebrew/opt/llvm/bin/clang++')
        self.compiler.set_executable('compiler_cxx', '/opt/homebrew/opt/llvm/bin/clang++')
        super().build_extensions()

extra_compile_args = [
    "-isysroot", "/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX15.2.sdk",
    "-std=c++17",
    "-stdlib=libc++",
    "-O0",
    "-fopenmp",
    "-I./metal-cpp",
    "-I./metal-cpp/common",
    "-fno-objc-arc",
    "-g"
]

extra_link_args = [
    "-isysroot", "/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX15.2.sdk",
    "-framework", "Metal",
    "-framework", "Foundation",
    "-framework", "MetalKit",
    "-framework", "CoreVideo",
    "-framework", "CoreGraphics",
    "-framework", "ImageIO",
    "-framework", "CoreServices",
    "-L/opt/homebrew/opt/libomp/lib",
    "-fopenmp"
]

ext_modules = [
    Extension(
        "mymodule",
        sources=[
            "src/metal_handler.mm",
            "metal-cpp/common/counter_thread.c",
            "metal-cpp/common/eviction.c",
        ],
        include_dirs=[pybind11.get_include()],
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
        language="objc++",  
    )
]

setup(
    name="mymodule",
    version="0.1",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
)
