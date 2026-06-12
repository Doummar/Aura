import json
import os

from aqt import mw


class AuraConfig:
    def __init__(self):
        self.path = os.path.join(mw.pm.profileFolder(), "aura_v5_config.json")
        self.data = {
            "sensitivity": 0.5,
            "pos": [50, 50],
            "study_min": 20,
            "break_min": 5,
            "long_break_min": 15,
            "long_break_every": 4,
            "show_hud": True,
            "display_mode": "aura",
            "show_focus_score": True,
            "show_cards_left": True,
            "show_progress_bar": True,
            "progress_bar_style": "bar",
            "warning_threshold": 40,
            "weight_again": -2,
            "weight_hard": -1,
            "weight_good": 1,
            "weight_easy": 0,
            "response_time_weight": 1,
            "ignore_easy_time": False,
            "first_run": True,
            "calibration_cards": 5,
            "show_session_summary": True,
            "continue_across_decks": False,
            "cross_deck_behavior": "continue",
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
            sensitivity = float(self.data.get("sensitivity", 0.5))
        except Exception:
            sensitivity = 0.5
        self.data["sensitivity"] = max(0.0, min(1.0, sensitivity))

        pos = self.data.get("pos", [50, 50])
        if not isinstance(pos, list) or len(pos) != 2:
            pos = [50, 50]
        self.data["pos"] = [
            self._clamp_int(pos[0], 50, -3000, 3000),
            self._clamp_int(pos[1], 50, -3000, 3000),
        ]

        self.data["study_min"] = self._clamp_int(self.data.get("study_min", 20), 20, 1, 120)
        self.data["break_min"] = self._clamp_int(self.data.get("break_min", 5), 5, 1, 60)
        self.data["long_break_min"] = self._clamp_int(
            self.data.get("long_break_min", 15), 15, 1, 180
        )
        self.data["long_break_every"] = self._clamp_int(
            self.data.get("long_break_every", 4), 4, 1, 20
        )
        self.data["show_hud"] = bool(self.data.get("show_hud", True))
        mode = str(self.data.get("display_mode", "aura")).lower()
        if mode not in ("aura", "pomodoro", "custom"):
            mode = "aura"
        self.data["display_mode"] = mode

        self.data["show_focus_score"] = bool(self.data.get("show_focus_score", True))
        self.data["show_cards_left"] = bool(self.data.get("show_cards_left", True))
        self.data["show_progress_bar"] = bool(self.data.get("show_progress_bar", True))

        if mode == "aura":
            self.data["show_focus_score"] = True
            self.data["show_cards_left"] = True
            self.data["show_progress_bar"] = True
        elif mode == "pomodoro":
            self.data["show_focus_score"] = False
            self.data["show_cards_left"] = False
            self.data["show_progress_bar"] = False

        bar_style = str(self.data.get("progress_bar_style", "bar")).lower()
        if bar_style not in ("dot", "bar"):
            bar_style = "bar"
        self.data["progress_bar_style"] = bar_style

        self.data["calibration_cards"] = self._clamp_int(
            self.data.get("calibration_cards", 5), 5, 3, 20
        )
        self.data["warning_threshold"] = self._clamp_int(
            self.data.get("warning_threshold", 40), 40, 20, 60
        )
        for key, default in [
            ("weight_again", -2), ("weight_hard", -1),
            ("weight_good",   1), ("weight_easy",  0),
        ]:
            self.data[key] = self._clamp_int(self.data.get(key, default), default, -2, 2)
        self.data["response_time_weight"] = self._clamp_int(
            self.data.get("response_time_weight", 1), 1, 0, 2
        )
        self.data["ignore_easy_time"] = bool(self.data.get("ignore_easy_time", False))
        self.data["first_run"] = bool(self.data.get("first_run", True))
        self.data["show_session_summary"] = bool(self.data.get("show_session_summary", True))
        self.data["continue_across_decks"] = bool(
            self.data.get("continue_across_decks", False)
        )
        cd_behavior = str(self.data.get("cross_deck_behavior", "continue")).lower()
        if cd_behavior not in ("pause", "continue"):
            cd_behavior = "continue"
        self.data["cross_deck_behavior"] = cd_behavior

    def load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as handle:
                    loaded = json.load(handle)
                if isinstance(loaded, dict):
                    self.data.update(loaded)
            except Exception:
                pass
        self._sanitize()

    def save(self):
        self._sanitize()
        try:
            with open(self.path, "w", encoding="utf-8") as handle:
                json.dump(self.data, handle, indent=4)
        except Exception:
            pass

    def get(self, key, default):
        return self.data.get(key, default)

    def set(self, key, val):
        self.data[key] = val
        self.save()
