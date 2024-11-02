# mflux-fasthtml

[![PyPI - Version](https://img.shields.io/pypi/v/mflux-fasthtml.svg)](https://pypi.org/project/mflux-fasthtml)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mflux-fasthtml.svg)](https://pypi.org/project/mflux-fasthtml)

A web app gui for [mflux](https://pypi.org/project/mflux/) python library implemented with [FastHTML](https://docs.fastht.ml)

-----

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [License](#license)

## Features

- async background generation with threads
- database for queueing up generation requests
- responsive web gui that will poll for completed generations and add to the display gallery

### Todo List

- fix bugs around interruptibility, exception handling
- memory management between model changes
- beautiful the web UI and improve UX
- support `mflux`'s existing Controlnet, Image-to-Image modes
- fast follow generation modes fast following `mflux` releases

## Installation

### Normal User Install

```sh
brew install uv
uv tool install mflux-fasthtml
cd /your/preferred/working/directory

# fixme: intended script interface, not working for now
mflux-fasthtml-app  
```

### Developer Install

```sh
# dev workaround: run the main.py
uv venv && source .venv/bin/activate
uv pip install -e .
python src/mflux_fasthtml/app/main.py
```

## License

`mflux-fasthtml` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
