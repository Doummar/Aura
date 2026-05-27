import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap


def _addon_root():
    return os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))


def _icons_dir():
    return os.path.join(os.path.dirname(__file__), 'icons')


def logo_path(size=64):
    candidates = [
        os.path.join(_icons_dir(), f'logo_{int(size)}.png'),
        os.path.join(_icons_dir(), 'logo.png'),
        os.path.join(_addon_root(), 'icon.png'),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return candidates[-1]


def logo_icon(size=32):
    return QIcon(logo_path(size))


def logo_pixmap(size=20):
    pix = QPixmap(logo_path(size))
    if pix.isNull():
        return QPixmap()
    return pix.scaled(
        size,
        size,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )
