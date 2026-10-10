"""Installed Metal resources for the SLAC native extension."""
from pathlib import Path


def library_path():
    """Locate the shader library independently of the current directory."""
    path = Path(__file__).resolve().with_name("default.metallib")
    if not path.is_file():
        raise FileNotFoundError(
            "SLAC's Metal resource is missing. Reinstall mymodule from a built wheel "
            "or build it from the source distribution with Xcode's Metal tools."
        )
    return str(path)
