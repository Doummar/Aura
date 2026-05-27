import json
import os

from aqt import mw


class AuraConfig:
    def __init__(self):
        self.path = os.path.join(mw.pm.profileFolder(), 'aura_v5_config.json')
        self.data = {
            'sensitivity': 0.5,
            'pos': [50, 50],
            'study_min': 20,
            'break_min': 5,
            'long_break_min': 15,
            'long_break_every': 4,
            'show_hud': True,
            'calibration_cards': 5,
            'show_session_summary': True,
        }
        self.load()

    def _clamp_int(self, value, default, min_value, max_value):
        try:
            n = int(value)
        except Exception:
            return default
        return max(min_value, min(max_value, n))

    def _sanitize(self):
        try:
            sensitivity = float(self.data.get('sensitivity', 0.5))
        except Exception:
            sensitivity = 0.5
        self.data['sensitivity'] = max(0.0, min(1.0, sensitivity))

        pos = self.data.get('pos', [50, 50])
        if not isinstance(pos, list) or len(pos) != 2:
            pos = [50, 50]
        self.data['pos'] = [
            self._clamp_int(pos[0], 50, -3000, 3000),
            self._clamp_int(pos[1], 50, -3000, 3000),
        ]

        self.data['study_min'] = self._clamp_int(self.data.get('study_min', 20), 20, 1, 120)
        self.data['break_min'] = self._clamp_int(self.data.get('break_min', 5), 5, 1, 60)
        self.data['long_break_min'] = self._clamp_int(self.data.get('long_break_min', 15), 15, 1, 180)
        self.data['long_break_every'] = self._clamp_int(self.data.get('long_break_every', 4), 4, 1, 20)
        self.data['show_hud'] = bool(self.data.get('show_hud', True))
        self.data['calibration_cards'] = self._clamp_int(self.data.get('calibration_cards', 5), 5, 3, 20)
        self.data['show_session_summary'] = bool(self.data.get('show_session_summary', True))

    def load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, 'r', encoding='utf-8') as handle:
                    loaded = json.load(handle)
                if isinstance(loaded, dict):
                    self.data.update(loaded)
            except Exception:
                pass
        self._sanitize()

    def save(self):
        self._sanitize()
        try:
            with open(self.path, 'w', encoding='utf-8') as handle:
                json.dump(self.data, handle, indent=4)
        except Exception:
            pass

    def get(self, key, default):
        return self.data.get(key, default)

    def set(self, key, val):
        self.data[key] = val
        self.save()
