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


class SessionSummaryDialog(QDialog):
    def __init__(self, summary, parent=None):
        super().__init__(parent)
        self.summary = summary or {}

        self.setWindowTitle('Aura: Session Summary')
        self.setMinimumWidth(390)
        self.setModal(True)
        self.setStyleSheet(
            """
            QDialog { background: #f7f7f7; }
            QLabel { color: #1f1f1f; font-size: 12px; font-family: 'Segoe UI'; }
            QLabel#title { font-size: 16px; font-weight: 700; color: #111111; }
            QLabel#subtitle { color: #3a3a3a; font-size: 12px; }
            QLabel[class='metric-label'] { color: #4a4a4a; font-size: 12px; }
            QLabel[class='metric-value'] { color: #111111; font-size: 12px; font-weight: 700; }
            QLabel#focus-trend { color: #111111; font-size: 12px; font-weight: 700; }
            QFrame#card { background: #ffffff; border: 1px solid #d8d8d8; border-radius: 6px; }
            QFrame#sep { background: #d8d8d8; min-height: 1px; max-height: 1px; border: none; }
            QPushButton#done {
                background: #2e6de0; color: #ffffff; border: none;
                border-radius: 5px; padding: 6px 16px; font-weight: 700;
            }
            """
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(10)

        title = QLabel('Session complete')
        title.setObjectName('title')
        root.addWidget(title)

        subtitle = QLabel('Nice work. You reached the end of this review session.')
        subtitle.setObjectName('subtitle')
        subtitle.setWordWrap(True)
        root.addWidget(subtitle)

        sep = QFrame()
        sep.setObjectName('sep')
        root.addWidget(sep)

        card = QFrame()
        card.setObjectName('card')
        grid = QGridLayout(card)
        grid.setContentsMargins(12, 10, 12, 10)
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(6)
        root.addWidget(card)

        self._metric(grid, 0, 'Cards studied', f"{int(self.summary.get('cards', 0))}")
        self._metric(grid, 1, 'Average score', f"{float(self.summary.get('avg_score', 50.0)):.1f}%")
        self._metric(grid, 2, 'Stability', f"{float(self.summary.get('stability', 50.0)):.1f}%")
        self._metric(grid, 3, 'Pause time', f"{float(self.summary.get('paused_minutes', 0.0)):.1f} min")

        best_focus = float(self.summary.get('best_focus_minutes', 0.0))
        avg_focus = float(self.summary.get('avg_focus_streak_minutes', 0.0))
        grid.addWidget(self._label('Best focus streak', 'metric-label'), 4, 0)
        trend = QLabel(self._focus_vs_avg_text(best_focus, avg_focus))
        trend.setObjectName('focus-trend')
        trend.setTextFormat(Qt.TextFormat.RichText)
        grid.addWidget(trend, 4, 1, alignment=Qt.AlignmentFlag.AlignRight)

        self._metric(grid, 5, 'Long breaks taken', f"{int(self.summary.get('long_breaks', 0))}")

        actions = QHBoxLayout()
        actions.addStretch()
        done_btn = QPushButton('Done')
        done_btn.setObjectName('done')
        done_btn.clicked.connect(self.accept)
        actions.addWidget(done_btn)
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
