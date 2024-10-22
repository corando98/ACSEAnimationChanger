import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but some modules need help.
build_exe_options = {
    "packages": [
        "os", "flask", "requests", "urllib3", "moviepy.editor",
        "moviepy.video.fx", "moviepy.video.io", "moviepy.audio.fx", "moviepy.audio.io"
    ],
    "includes": ["jinja2.ext"],
    "include_files": ["videos/"]
}

# Base is set to "Win32GUI" for a GUI application
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="FlaskApp",
    version="0.1",
    description="My Flask App",
    options={"build_exe": build_exe_options},
    executables=[Executable("app.py", base=base)]
)
