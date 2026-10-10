"""Build the native module and its Metal resource from the same source tree."""
import os
from pathlib import Path
import subprocess
import sys

# Set this before setuptools initializes the platform/build configuration.
os.environ.setdefault("MACOSX_DEPLOYMENT_TARGET", "14.0")

import pybind11
from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext as _build_ext
from setuptools.command.build_py import build_py as _build_py


def xcrun(*arguments):
    return subprocess.check_output(
        ["xcrun", "--sdk", "macosx", *arguments], text=True
    ).strip()


class build_py(_build_py):
    def run(self):
        super().run()
        resource = Path(self.build_lib) / "slac_resources" / "default.metallib"
        resource.parent.mkdir(parents=True, exist_ok=True)
        temporary = Path(self.get_finalized_command("build_ext").build_temp) / "metal"
        temporary.mkdir(parents=True, exist_ok=True)
        cache = temporary / "module-cache"
        cache.mkdir(exist_ok=True)
        air = temporary / "slac.air"
        target = os.environ.get("MACOSX_DEPLOYMENT_TARGET", "14.0")
        subprocess.run(
            ["xcrun", "--sdk", "macosx", "metal",
             f"-mmacosx-version-min={target}",
             f"-fmodules-cache-path={cache.resolve()}",
             "-c", "src/add.metal", "-o", str(air)], check=True
        )
        subprocess.run(
            ["xcrun", "--sdk", "macosx", "metallib", str(air),
             "-o", str(resource)], check=True
        )

    def get_outputs(self, include_bytecode=True):
        outputs = super().get_outputs(include_bytecode)
        outputs.append(str(Path(self.build_lib) / "slac_resources" / "default.metallib"))
        return outputs


class build_ext(_build_ext):
    def build_extensions(self):
        if sys.platform != "darwin":
            raise RuntimeError("SLAC requires Apple Silicon macOS and Xcode with Metal tools.")
        compiler = xcrun("--find", "clang++")
        sdk = xcrun("--show-sdk-path")
        self.compiler.src_extensions.append(".mm")
        self.compiler.set_executable("compiler_so", [compiler, "-x", "objective-c++"])
        self.compiler.set_executable("compiler_cxx", compiler)
        self.compiler.set_executable("linker_so", [compiler, "-bundle", "-undefined", "dynamic_lookup"])
        target = "-mmacosx-version-min=" + os.environ["MACOSX_DEPLOYMENT_TARGET"]
        for extension in self.extensions:
            extension.extra_compile_args += ["-isysroot", sdk, target]
            extension.extra_link_args += ["-isysroot", sdk, target]
        super().build_extensions()


setup(
    ext_modules=[Extension(
        "mymodule",
        sources=["src/metal_handler.mm", "metal-cpp/common/counter_thread.c",
                 "metal-cpp/common/eviction.c"],
        include_dirs=[pybind11.get_include(), "."],
        # Cache helpers contain C++ casts; OpenMP is not used by these sources.
        extra_compile_args=["-std=c++17", "-stdlib=libc++",
                            "-O0", "-fno-objc-arc", "-g0"],
        extra_link_args=["-framework", "Metal", "-framework", "Foundation",
                         "-framework", "IOKit"],
        language="c++",
    )],
    cmdclass={"build_ext": build_ext, "build_py": build_py},
)
