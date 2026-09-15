# StemCNV runtime image

This image contains guarantees no problems anymore with StemCNV-check though a portable architecture on any OS. 

---

## Tutorial

### Downloads

#### Python
* [Python 3.13.13 64bit win](https://www.python.org/ftp/python/3.13.15/python-3.13.15-amd64.exe)
* [Python 3.13.13 macOS](https://www.python.org/ftp/python/3.13.13/python-3.13.13-macos11.pkg)

#### Docker
* [DOCKER macOS Apple Silicon](https://desktop.docker.com/mac/main/arm64/Docker.dmg?utm_source=docker&utm_medium=webreferral&utm_campaign=docs-driven-download-mac-arm64)
* [DOCKER macOS Intel](https://desktop.docker.com/mac/main/amd64/Docker.dmg?utm_source=docker&utm_medium=webreferral&utm_campaign=docs-driven-download-mac-amd64)

#### VS Code (JUST FOR CMD (super simple!))
* [Visual Studio Code Windows (x64)](https://code.visualstudio.com/sha/download?build=stable&os=win32-x64-user)
* [Visual Studio Code macOS](https://code.visualstudio.com/sha/download?build=stable&os=darwin-universal)

#### Git
* [Git Windows](https://git-scm.com/download/win)
* [Git macOS (Universal Binary Installer / Homebrew)](https://git-scm.com/download/mac)

#### EXAMPLE DATASET
* [Example data](https://zenodo.org/records/16962381/files/example_input_data.zip?download=1)

---

### Installation

Instalations finisshed...

- Open VS CODE
- Click: **Clone Repository** -> https://github.com/wired87/scnv_base.git -> enter (New window pops up, this is your Frontend)

- Create new terminal:
   Header bar left -> **Terminal** -> **New Terminal** (window should pop up)
- Paste the following CMD:

```bash
python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
```

Now drag the unzipped example_input_data folder inside the project root (where the Dockerfile is located) 

To start the enigne just run (inside stemcnvui (mavigate with cd stemcnvui))
```bash
source venv/bin/activate && python3 -m startup
```

#
#

#### This Project is funded by the German 
***Federal Agency of Work***

in cooperation with the

***JobCenter***

