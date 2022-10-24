#!/usr/bin/env python3
import base64
import os
import platform
import stat
import sys
from pathlib import Path

from imagesubtractor import run_app
from imagesubtractor.icon import ICON_DATA


def make_short_cut():
    file = Path(__file__).resolve()
    home = file.parent
    icon_dir = home.joinpath("icon")
    if not icon_dir.exists():
        icon_dir.mkdir()
    icon_file = icon_dir.joinpath("icon.png")
    if not icon_file.exists():
        with open(icon_file, "wb") as file:
            file.write(base64.b64decode(ICON_DATA))

    p = platform.system()
    if p == "Linux":
        launch_file = home.joinpath("Subtractor.desktop")
        if launch_file.exists() or launch_file.is_file():
            return

        ENV_PATH = str(Path(sys.executable).parent.resolve()) + ":$PATH"
        launch_str = [
            "[Desktop Entry]",
            "Name=Subtractor",
            f"Exec=env PATH='{ENV_PATH}' {str(file)}",
            "Comment=",
            "Terminal=false",
            f"Icon={str(icon_file)}",
            "Type=Application",
        ]
        launch_file.write_text("\n".join(launch_str))

        st = os.stat(launch_file)
        os.chmod(launch_file, st.st_mode | stat.S_IEXEC)

    elif p == "Darwin":
        ...
    else:
        ...


#try:
#    make_short_cut()
#except Exception:
#    pass
#
if __name__ == "__main__":
    run_app()
