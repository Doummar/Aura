# Aura Minimal Focus HUD
# Created by Adel Aitah
# GitHub: https://github.com/Doummar/Aura
# Copyright (c) 2026 Adel Aitah — All rights reserved
"""
Aura Minimal Focus HUD — Anki
Aura adds a minimal live focus HUD to your Anki review sessions, helping you stay aware of your pacing, consistency, and focus rhythm without cluttering the screen.
"""

ADDON_NAME = "Aura Minimal Focus HUD"
ADDON_AUTHOR  = "Adel Aitah"
ADDON_VERSION = "1.0.1"
ADDON_URL     = "https://github.com/Doummar/Aura"
HANDLE = 12

from .core.initializer import init

init()
