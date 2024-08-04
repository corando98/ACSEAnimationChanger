import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but some modules need help.
build_exe_options = {
    "packages": [
        "os", "flask", "requests", "urllib3", "moviepy.editor",
        "moviepy.video.fx", "moviepy.video.io", "moviepy.audio.fx", "moviepy.audio.io"
    ],
    "includes": ["jinja2.ext"],
    "include_files": ["videos/", "icon.ico"]
}

# Base is set to "Console" to keep the console window open for debugging
base = "Console" if sys.platform == "win32" else None

setup(
    name="ACSE Animation Changer",
    version="0.1",
    description="ACSE Animation Changer",
    options={"build_exe": build_exe_options},
    executables=[Executable("app.py", base=base, icon="icon.ico")]
)
