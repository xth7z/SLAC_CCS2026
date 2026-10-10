"""Check the contents of built archives without starting hardware collection."""
import argparse
from email.parser import BytesParser
from pathlib import Path
import tarfile
import zipfile


def check(dist, source):
    archives = list(dist.glob("*.tar.gz"))
    wheels = list(dist.glob("*.whl"))
    assert len(archives) == 1 and wheels, "Expected one source archive and at least one wheel"
    licenses = ["LICENSE", "THIRD_PARTY_NOTICES.md"] + [
        path.relative_to(source).as_posix() for path in sorted((source / "licenses").glob("*.txt"))
    ]
    assert len(licenses) == 8, "Missing third-party license texts"
    with tarfile.open(archives[0]) as archive:
        files = {member.name.partition("/")[2]: archive.extractfile(member).read()
                 for member in archive.getmembers() if member.isfile()}
    required = {"pyproject.toml", "setup.py", "MANIFEST.in", "README.md",
                "src/add.metal", "src/metal_handler.mm", "src/slac_resources/__init__.py"}
    required.update(path.relative_to(source).as_posix()
                    for path in (source / "metal-cpp").rglob("*") if path.is_file())
    for name in required | set(licenses):
        assert files[name] == (source / name).read_bytes(), f"Missing or stale source: {name}"
    assert not any(name.endswith((".air", ".metallib", ".so")) for name in files), "Stale binary in sdist"

    for wheel in wheels:
        with zipfile.ZipFile(wheel) as archive:
            names = archive.namelist()
            metadata_name, = [name for name in names if name.endswith(".dist-info/METADATA")]
            info = metadata_name.removesuffix("METADATA")
            metadata = BytesParser().parsebytes(archive.read(metadata_name))
            assert metadata["Version"] == "0.2.0"
            assert metadata["License-Expression"] == "MIT AND Apache-2.0 AND BSD-3-Clause"
            assert "Tianhong Xu" in metadata["Author-email"]
            assert "Your Name" not in str(metadata)
            assert set(metadata.get_all("License-File")) == set(licenses)
            for name in licenses:
                assert archive.read(info + "licenses/" + name) == (source / name).read_bytes(), name
            assert archive.read("slac_resources/default.metallib").startswith(b"MTLB")
            assert len([name for name in names if name.startswith("mymodule.") and name.endswith(".so")]) == 1
            assert not any(name.endswith(".air") for name in names)
        print(f"Verified sources, metadata, licenses, and Metal resource: {wheel.name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist", type=Path, default=Path("dist"))
    args = parser.parse_args()
    check(args.dist.resolve(), Path(__file__).resolve().parents[1])
