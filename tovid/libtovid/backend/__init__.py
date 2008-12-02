#! /usr/bin/env python
# __init__.py (backend)

"""Backends, which do some task using a command-line program.

This module is split into submodules, each named after the command-line
program they predominantly rely on. Backends which use several of these
submodules are defined here in ``__init__.py``.
"""

# Submodules
__all__ = [
    'ffmpeg',
    'mpeg2enc',
    'mplayer',
    'mplex',
    'spumux',
    'transcode',
]
