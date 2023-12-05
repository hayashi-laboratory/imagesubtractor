# Image Subtractor User Interface

<p>
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
<a href="https://github.com/lycantrope/imagesubtractor/blob/main/License"><img alt="license: GPL-3.0" src="https://img.shields.io/github/license/lycantrope/imagesubtractor.svg"></a>
</p>

This application is code refactoring of `imagesubtandmeasure.py` created by Taizo Kawano.

## Requirements

- python >= 3.7.10
- opencv-python-headless
- pandas
- numpy
- PySide2


## Installation and running

### pip environment (Linux/MacOS)
- Installation:
```Shell
~$ python3 -m venv .venv

~$ source .venv/bin/activate

(.venv) ~$ pip install -U git+https://github.com/lycantrope/imagesubtractor
```
- Running application:

```Shell
~$ source .venv/bin/activate
(.venv) ~$ imagesubtractor
```

### pip environment (Windows)
- Installation:

```PowerShell
> python3 -m venv .venv

> .\.venv\Scripts\activate.bat

(.venv)> pip install -U git+https://github.com/lycantrope/imagesubtractor
```
- Running application:

```PowerShell
> .\.venv\Scripts\activate.bat
(.venv)> imagesubtractor
```
