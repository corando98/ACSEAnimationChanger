# ACSE Animation Changer

ACSE Animation Changer is a tool designed to manage and replace boot animations for Armoury Crate 1.5 system. It allows users to download, preview, convert, and replace boot animation videos.

## Features

- Download videos from the SteamDeckRepo.
- Preview downloaded videos.
- Convert videos to MP4 format.
- Replace boot animations with the selected video.
- Delete unwanted videos.

## Installation

### Pre-built Binary

A pre-built binary is available in the [releases](https://github.com/yourusername/acse-animation-changer/releases) section. Simply download the zip file, unzip it, and run the `app.exe` file.



### Building from Source

## Requirements

- Python 3.x (if building from source)
- Flask
- requests
- urllib3
- moviepy
- jinja2
- cx_Freeze


1. **Clone the Repository:**
    ```sh
    git clone https://github.com/yourusername/acse-animation-changer.git
    cd acse-animation-changer
    ```

2. **Install Dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

3. **Download and Place Icon:**
    - Create an icon file (`.ico`) and place it in the project directory as `icon.ico`.

4. **Project Structure:**
    Ensure your project structure looks like this:
    ```
    your_project/
    │
    ├── app.py
    ├── setup.py
    ├── icon.ico
    ├── README.md
    └── videos/
    ```

### Building the Executable

1. **Update `setup.py`:**

    ```python
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
    ```

2. **Build the Executable:**

    ```sh
    python setup.py build
    ```

3. **Run the Executable:**
    After the build process completes, navigate to the `build/exe.win-amd64-3.x` directory and run the generated `app` file. The console will remain open, showing debugging information.

## Usage

1. **Download Videos:**
    - Use the "Download Videos" tab to search for and download videos from the SteamDeckRepo.

2. **Manage Videos:**
    - Use the "Manage Videos" tab to preview, convert, replace, or delete downloaded videos.

3. **Replace Path:**
    - Specify the path to replace or leave it empty to auto-detect the path for replacing the boot animation.

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.

## License

This project is licensed under the MIT License.
