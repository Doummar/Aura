from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QFrame, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QVBoxLayout, QWidget,
)


# ── Collapsible section widget ────────────────────────────────────────────────

_HDR = """
    QPushButton {
        text-align: left;
        padding: 7px 10px;
        border: none;
        border-bottom: 1px solid #d4d4d4;
        background: #f0f0f0;
        font-weight: bold;
        font-size: 12px;
        color: #1a1a1a;
    }
    QPushButton:hover:!checked { background: #e6e6e6; }
    QPushButton:checked {
        background: palette(highlight);
        color: palette(highlighted-text);
        border-bottom: 1px solid palette(highlight);
    }
"""

_BODY = (
    "font-family:'Segoe UI',sans-serif; font-size:12px; color:#111; "
    "background:#ffffff; padding:8px 14px 10px 14px;"
)


class _Section(QWidget):
    def __init__(self, title: str, html: str, parent=None):
        super().__init__(parent)
        self._title = title
        v = QVBoxLayout(self)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)

        self._btn = QPushButton(f"▶   {title}")
        self._btn.setCheckable(True)
        self._btn.setStyleSheet(_HDR)
        self._btn.setCursor(Qt.CursorShape.PointingHandCursor)
        v.addWidget(self._btn)

        self._body = QLabel(html)
        self._body.setWordWrap(True)
        self._body.setTextFormat(Qt.TextFormat.RichText)
        self._body.setStyleSheet(_BODY)
        self._body.setVisible(False)
        v.addWidget(self._body)

        self._btn.toggled.connect(self._toggle)

    def _toggle(self, on: bool):
        self._body.setVisible(on)
        self._btn.setText(("▼" if on else "▶") + f"   {self._title}")


# ── Content helpers ───────────────────────────────────────────────────────────

def _b(text):   return f"<b>{text}</b>"
def _dim(text): return f'<span style="color:#666;font-size:11px">{text}</span>'
def _row(text): return f"<p style='margin:2px 0'>{text}</p>"

def _rows(*items):
    return "".join(_row(f"&bull;&nbsp; {i}") for i in items)


# ── Section content ───────────────────────────────────────────────────────────

_SECTIONS = [

    ("HOW IT WORKS", _rows(
        "Aura starts automatically when a review begins and stops when it ends.",
        f"{_b('Aura HUD')} — full overlay: timer &middot; rhythm % &middot; rhythm bar &middot; cards left.",
        f"{_b('Pomodoro only')} — timer and break states only. Rhythm is not tracked.",
        f"{_b('Custom')} — you choose exactly which elements appear on the HUD.",
        "The session summary appears only when the deck reaches 0 cards.",
    )),

    ("BREAK CYCLE", _rows(
        "Study block &rarr; short break &rarr; study &rarr; &hellip; &rarr; long break every N sessions.",
        "Aura asks before each break starts and again before returning to study.",
        f"The HUD shows a {_b('Break')} or {_b('Long Break')} tag during breaks.",
    )),

    ("HUD CONTROLS", _rows(
        f"Click the {_b('time display')} to pause or resume the timer.",
        f"Press and hold the {_b('time display')} for ~0.6 s to reset the timer back to zero.",
        "Drag from any non-time area on the HUD to reposition it.",
        f"A {_b('Paused')} tag appears while the timer is paused.",
    )),

    ("RHYTHM SCORE", _rows(
        "Not a grade &mdash; an estimate of focus rhythm based on how you answer.",
        f"{_b('50 %')} is the neutral baseline. A steady session hovers here.",
        "Above 50 % means good flow. Below means rhythm is slipping.",
        "The score takes a few cards to calibrate &mdash; set by Calibration cards.",
    )),

    ("ANSWER WEIGHTS", _rows(
        "Each Anki button has a weight from &minus;2 to +2 that you set yourself.",
        "The average weight across recent cards moves the score up or down.",
        f"Defaults: {_b('Again &minus;2 &middot; Hard &minus;1 &middot; Good +1 &middot; Easy 0')}",
        _dim("Set Easy to &minus;1 if pressing it means skipping cards too fast."),
        _dim("Set Again to &minus;1 if drilling hard new material where Again is expected."),
    )),

    ("RESPONSE TIME", _rows(
        "How quickly and consistently you answer also influences the score.",
        f"Set Response time to {_b('Off')} for audio, image, or speaking card decks.",
        f"{_b('Ignore Easy for response time')} excludes Easy cards from timing only.",
        "&times;1 is the default influence. &times;2 doubles the timing contribution.",
    )),

    ("COLOUR SCALE", _rows(
        f'Below warning threshold &rarr; <b style="color:#b91c1c">red</b> &mdash; rhythm has dropped.',
        "Threshold to threshold + 9 % &rarr; smooth red &rarr; orange &rarr; amber &rarr; green.",
        f'Above threshold + 9 % &rarr; <b style="color:#16a34a">green</b>, deepening as score rises.',
        _dim("Default threshold is 40 %. Raise it if you want an earlier warning."),
    )),

    ("ALL SETTINGS", (
        _row(_b("Timer tab"))
        + _rows(
            "Display mode &mdash; Aura HUD, Pomodoro only, or Custom.",
            "Study / Short break / Long break &mdash; durations in minutes.",
            "Sessions before long break &mdash; study blocks between long breaks.",
            "Continue timer across decks &mdash; keeps the timer alive when switching decks.",
            "Between decks &mdash; pause the timer automatically between decks, or keep it running.",
        )
        + _row(_b("Display tab"))
        + _rows(
            "Show HUD overlay &mdash; toggle the entire overlay on or off.",
            "Show focus rhythm % &mdash; the rhythm score as a number.",
            "Show cards left &mdash; remaining card count on the HUD.",
            "Show rhythm bar &mdash; colour indicator (Dot or Bar style).",
            "Show session summary &mdash; recap when the deck reaches 0 cards.",
        )
        + _row(_b("Rhythm tab"))
        + _rows(
            "Again / Hard / Good / Easy &mdash; weight each button (&minus;2 to +2).",
            "Reaction speed &mdash; how quickly the score reacts to recent answers.",
            "Calibration cards &mdash; answers needed before the score is trusted.",
            "Warning threshold &mdash; score where the dot turns red (20&ndash;60 %).",
            "Response time &mdash; influence of answer speed (Off &middot; &times;1 &middot; &times;2).",
            "Ignore Easy for response time &mdash; exclude Easy cards from timing.",
        )
    )),

    ("TIPS", _rows(
        f"Drilling hard new cards? Lower {_b('Again')} to &minus;1 to be less punishing.",
        f"Using Easy to skip known cards? Set {_b('Easy')} to &minus;1 to flag that.",
        f"Want green only when truly above baseline? Raise {_b('Warning threshold')} to 50 %.",
        f"Audio or image decks? Set {_b('Response time')} to Off.",
        f"{_b('Reset weights')} (Rhythm tab) &mdash; restores only the four button weights.",
        f"{_b('Reset to Default')} (Help tab) &mdash; restores every setting.",
    )),

]


# ── Dialog ────────────────────────────────────────────────────────────────────

class HelpWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Aura - Guide")
        self.setMinimumWidth(420)
        self.resize(460, 520)
        self.setStyleSheet("""
            QDialog   { background: #f6f6f6; }
            QWidget#container { background: #f6f6f6; }
            QScrollArea { border: none; background: #f6f6f6; }
            QPushButton#close-btn {
                background: #2e6de0; color: #ffffff; border: none;
                border-radius: 3px; padding: 5px 20px;
                font-weight: bold; font-size: 12px;
            }
            QPushButton#close-btn:hover { background: #2558c4; }
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(6)

        # Header
        title_lbl = QLabel("Aura: Minimal HUD")
        title_lbl.setStyleSheet(
            "font-size:16px; font-weight:bold; color:#0f0f0f;"
        )
        root.addWidget(title_lbl)
        sub_lbl = QLabel("Click any section to expand.")
        sub_lbl.setStyleSheet("font-size:12px; color:#444;")
        root.addWidget(sub_lbl)

        # Accordion in a scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        container.setObjectName("container")
        cl = QVBoxLayout(container)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(1)

        for title, html in _SECTIONS:
            cl.addWidget(_Section(title, html))

        cl.addStretch()
        scroll.setWidget(container)
        root.addWidget(scroll, 1)

        # ── Separator ─────────────────────────────────────────────────────
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.Shape.HLine)
        sep1.setStyleSheet("color: #d0d0d0;")
        root.addWidget(sep1)

        # ── Buttons ───────────────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(0, 4, 0, 4)
        settings_btn = QPushButton("Open Settings")
        settings_btn.clicked.connect(self._open_settings)
        btn_row.addWidget(settings_btn)
        btn_row.addStretch()
        got_it_btn = QPushButton("Got it  ✓")
        got_it_btn.setObjectName("close-btn")
        got_it_btn.clicked.connect(self.accept)
        btn_row.addWidget(got_it_btn)
        root.addLayout(btn_row)

        # ── Separator ─────────────────────────────────────────────────────
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet("color: #d0d0d0;")
        root.addWidget(sep2)

        # ── Version line ──────────────────────────────────────────────────
        ver = QLabel("<b>Aura</b>  v1.0.1 &mdash; Created by Adel")
        ver.setStyleSheet("font-size:11px; color:#555; padding: 2px 0;")
        root.addWidget(ver)

    def _open_settings(self):
        self.done(0)
        from aqt import mw
        if hasattr(mw, "aura_v5_active"):
            from .settings_window import SettingsWindow
            SettingsWindow(mw.aura_v5_active["config"], mw).exec()

