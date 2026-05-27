from PyQt6.QtWidgets import QDialog, QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout


class HelpWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Aura - Guide')
        self.setMinimumWidth(440)
        self.setStyleSheet(
            """
            QDialog { background: #f7f7f7; }
            QLabel { color: #111111; font-size: 12px; font-family: 'Segoe UI'; }
            QLabel#title { font-size: 17px; font-weight: 700; color: #111111; }
            QLabel.item { color: #111111; background: #ffffff; border: 1px solid #d8d8d8; border-radius: 6px; padding: 7px 9px; font-size: 12px; }
            QFrame#sep { background: #dddddd; min-height: 1px; max-height: 1px; border: none; }
            QPushButton#open-settings-btn { background: #ffffff; color: #222222; border: 1px solid #d2d2d2; border-radius: 5px; padding: 8px 16px; }
            QPushButton#got-it-btn { background: #2e6de0; color: #ffffff; border: none; border-radius: 5px; padding: 8px 16px; font-weight: 700; }
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 16, 22, 16)
        layout.setSpacing(7)

        title = QLabel('Aura: Minimal HUD')
        title.setObjectName('title')
        layout.addWidget(title)

        subtitle = QLabel('Simple live focus HUD for Anki review sessions.')
        subtitle.setStyleSheet('color:#222222; font-size:12px;')
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)
        layout.addWidget(self._line())

        layout.addWidget(self._section('HOW IT WORKS'))
        for txt in (
            'Starts automatically when review starts.',
            'Shows time, score, and cards left.',
            'Cycles between study, short breaks, and long breaks.',
            'Aura asks before a break starts and asks again before returning to study.',
            'Toolbar shows Break or Long Break tag during breaks.',
            'Session summary appears only when the deck reaches 0 cards left.',
        ):
            layout.addWidget(self._item(txt))

        layout.addWidget(self._section('PAUSE / RESUME'))
        for txt in (
            'Click the time text on HUD to pause.',
            'Click the time text again to resume.',
            'Timer and score state continue from exact same point.',
            'A PAUSED tag appears while Aura is paused.',
        ):
            layout.addWidget(self._item(txt))

        layout.addWidget(self._section('HOW SCORE WORKS'))
        for txt in (
            'Aura looks at your recent answer accuracy.',
            'Aura also checks if your response times are steady or jumpy.',
            'Score is smoothed over time so it does not jump too hard.',
            'Higher score means better focus rhythm.',
            'Sensitivity controls how quickly score reacts to changes.',
        ):
            layout.addWidget(self._item(txt))

        layout.addWidget(self._section('SETTINGS'))
        for txt in (
            'Sensitivity changes score volatility.',
            'Calibration cards sets how many answers are needed before scoring starts.',
            'Study and break minutes control cycle length.',
            'Long break minutes controls long break duration.',
            'Long break every N breaks controls long break frequency.',
            'Session summary shows average score, stability, pause time, and best focus streak.',
        ):
            layout.addWidget(self._item(txt))

        layout.addStretch()
        layout.addWidget(self._line())

        buttons = QHBoxLayout()
        open_settings_btn = QPushButton('Open Settings')
        open_settings_btn.setObjectName('open-settings-btn')
        open_settings_btn.clicked.connect(self.open_settings)
        buttons.addWidget(open_settings_btn)
        buttons.addStretch()
        got_it_btn = QPushButton('Got it')
        got_it_btn.setObjectName('got-it-btn')
        got_it_btn.clicked.connect(self.accept)
        buttons.addWidget(got_it_btn)
        layout.addLayout(buttons)

        layout.addWidget(self._line())
        footer = QLabel('<b>Aura</b>  v1.0.0  &mdash;  Created by Adel')
        footer.setStyleSheet('font-size:11px;color:#202020;')
        layout.addWidget(footer)

    def _line(self):
        line = QFrame()
        line.setObjectName('sep')
        line.setFrameShape(QFrame.Shape.HLine)
        return line

    def _section(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet('font-size:13px; font-weight:700; color:#303030; letter-spacing:0.2px; margin-top:4px; margin-bottom:2px;')
        return lbl

    def _item(self, text):
        lbl = QLabel(f'- {text}')
        lbl.setProperty('class', 'item')
        lbl.setWordWrap(True)
        return lbl

    def open_settings(self):
        self.done(0)
        from aqt import mw
        if hasattr(mw, 'aura_v5_active'):
            from .settings_window import SettingsWindow
            diag = SettingsWindow(mw.aura_v5_active['config'], mw)
            diag.exec()
