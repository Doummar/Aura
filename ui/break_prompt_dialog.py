from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)


class BreakPromptDialog(QDialog):
    def __init__(self, kind, minutes, details, parent=None):
        super().__init__(parent)
        self.kind = str(kind).upper()
        self.minutes = max(1, int(minutes))
        self.details = details or {}

        self.setWindowTitle('Aura: Break Time')
        self.setMinimumWidth(390)
        self.setModal(True)
        self.setStyleSheet(
            """
            QDialog { background: #f7f7f7; }
            QLabel { color: #1f1f1f; font-size: 12px; font-family: 'Segoe UI'; }
            QLabel#section-title { font-size: 12px; color: #3a3a3a; }
            QLabel[class='metric-label'] { color: #4a4a4a; font-size: 12px; }
            QLabel[class='metric-value'] { color: #111111; font-size: 12px; font-weight: 700; }
            QLabel#question { font-size: 16px; font-weight: 700; color: #111111; }
            QLabel#focus-trend { color: #111111; font-size: 12px; font-weight: 700; }
            QFrame#card { background: #ffffff; border: 1px solid #d8d8d8; border-radius: 6px; }
            QFrame#sep { background: #d8d8d8; min-height: 1px; max-height: 1px; border: none; }
            QPushButton#skip {
                background: #ffffff; color: #222222; border: 1px solid #cfcfcf;
                border-radius: 5px; padding: 6px 14px; min-width: 92px;
            }
            QPushButton#start {
                background: #2e6de0; color: #ffffff; border: none;
                border-radius: 5px; padding: 6px 14px; font-weight: 700; min-width: 165px;
            }
            """
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(10)

        section = QLabel('Session')
        section.setObjectName('section-title')
        root.addWidget(section)

        card = QFrame()
        card.setObjectName('card')
        grid = QGridLayout(card)
        grid.setContentsMargins(12, 10, 12, 10)
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(6)
        root.addWidget(card)

        self._metric(grid, 0, 'Cards studied', str(int(self.details.get('cards', 0))))
        self._metric(grid, 1, 'Average score', f"{float(self.details.get('avg_score', 50.0)):.1f}%")
        self._metric(grid, 2, 'Stability', f"{float(self.details.get('stability', 50.0)):.1f}%")

        focus = float(self.details.get('best_focus_minutes', 0.0))
        avg_focus = float(self.details.get('avg_focus_streak_minutes', 0.0))
        grid.addWidget(self._label('Best focus streak', 'metric-label'), 3, 0)
        trend = QLabel(self._focus_vs_avg_text(focus, avg_focus))
        trend.setObjectName('focus-trend')
        trend.setTextFormat(Qt.TextFormat.RichText)
        grid.addWidget(trend, 3, 1, alignment=Qt.AlignmentFlag.AlignRight)

        sep = QFrame()
        sep.setObjectName('sep')
        root.addWidget(sep)

        kind_text = 'long ' if self.kind == 'LONG' else ''
        question = QLabel(f'Take a {self.minutes}-min {kind_text}break?')
        question.setObjectName('question')
        root.addWidget(question)

        actions = QHBoxLayout()
        actions.setSpacing(10)
        skip_btn = QPushButton('Skip break')
        skip_btn.setObjectName('skip')
        skip_btn.clicked.connect(self.reject)
        start_btn = QPushButton(f'Start {self.minutes}-min break ->')
        start_btn.setObjectName('start')
        start_btn.clicked.connect(self.accept)
        actions.addWidget(skip_btn)
        actions.addStretch()
        actions.addWidget(start_btn)
        root.addLayout(actions)

    def _label(self, text, klass):
        lbl = QLabel(str(text))
        lbl.setProperty('class', klass)
        return lbl

    def _metric(self, grid, row, name, value):
        grid.addWidget(self._label(name, 'metric-label'), row, 0)
        grid.addWidget(self._label(value, 'metric-value'), row, 1, alignment=Qt.AlignmentFlag.AlignRight)

    def showEvent(self, event):
        super().showEvent(event)
        self._center_on_parent_window()

    def _center_on_parent_window(self):
        parent = self.parentWidget()
        if parent is not None:
            parent_window = parent.window()
            if parent_window is not None:
                frame = self.frameGeometry()
                frame.moveCenter(parent_window.frameGeometry().center())
                self.move(frame.topLeft())
                return

        screen = self.screen() or QApplication.primaryScreen()
        if screen is not None:
            frame = self.frameGeometry()
            frame.moveCenter(screen.availableGeometry().center())
            self.move(frame.topLeft())

    def _focus_vs_avg_text(self, best_minutes, avg_minutes):
        diff = float(best_minutes) - float(avg_minutes)
        if diff >= 0:
            arrow = '\u2191'
            color = '#15803d'
            sign = '+'
        else:
            arrow = '\u2193'
            color = '#b91c1c'
            sign = '-'

        return (
            f"{best_minutes:.1f} min "
            f"<span style='color:{color};'>{arrow} {sign}{abs(diff):.1f} min</span> "
            f"avg {avg_minutes:.1f} min"
        )
