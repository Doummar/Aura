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

        self.setWindowTitle("Aura: Break Time")
        self.setMinimumWidth(390)
        self.setModal(True)
        self.setStyleSheet(
            """
            QDialog { background: #f7f7f7; }
            QLabel { color: #1f1f1f; font-size: 12px; font-family: "Segoe UI"; }
            QLabel#section-title { font-size: 12px; color: #3a3a3a; }
            QLabel[class="metric-label"] { color: #4a4a4a; font-size: 12px; }
            QLabel[class="metric-value"] { color: #111111; font-size: 12px; font-weight: 700; }
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

        show_cards = bool(self.details.get("show_cards_stats", True))
        show_focus = bool(self.details.get("show_focus_stats", True))

        if show_cards or show_focus:
            section = QLabel("Session")
            section.setObjectName("section-title")
            root.addWidget(section)

            card = QFrame()
            card.setObjectName("card")
            card_layout = QGridLayout(card)
            card_layout.setContentsMargins(12, 10, 12, 10)
            card_layout.setHorizontalSpacing(16)
            card_layout.setVerticalSpacing(6)
            root.addWidget(card)

            row = 0
            if show_cards:
                card_layout.addWidget(self._label("Cards studied", "metric-label"), row, 0)
                card_layout.addWidget(
                    self._label(str(int(self.details.get("cards", 0))), "metric-value"),
                    row,
                    1,
                    alignment=Qt.AlignmentFlag.AlignRight,
                )
                row += 1

            if show_focus:
                avg_score = float(self.details.get("avg_score", 50.0))
                card_layout.addWidget(self._label("Focus rhythm", "metric-label"), row, 0)
                card_layout.addWidget(
                    self._label(f"{avg_score:.1f}%", "metric-value"),
                    row,
                    1,
                    alignment=Qt.AlignmentFlag.AlignRight,
                )
                row += 1

                stability = float(self.details.get("stability", 50.0))
                card_layout.addWidget(self._label("Rhythm stability", "metric-label"), row, 0)
                card_layout.addWidget(
                    self._label(f"{stability:.1f}%", "metric-value"),
                    row,
                    1,
                    alignment=Qt.AlignmentFlag.AlignRight,
                )
                row += 1

                focus = float(self.details.get("best_focus_minutes", 0.0))
                avg_focus = float(self.details.get("avg_focus_streak_minutes", 0.0))
                card_layout.addWidget(self._label("Longest focused run", "metric-label"), row, 0)
                trend_label = QLabel(self._focus_vs_avg_text(focus, avg_focus))
                trend_label.setObjectName("focus-trend")
                trend_label.setTextFormat(Qt.TextFormat.RichText)
                card_layout.addWidget(trend_label, row, 1, alignment=Qt.AlignmentFlag.AlignRight)

            sep = QFrame()
            sep.setObjectName("sep")
            root.addWidget(sep)

        kind_text = "long " if self.kind == "LONG" else ""
        question = QLabel(f"Take a {self.minutes}-min {kind_text}break?")
        question.setObjectName("question")
        root.addWidget(question)

        actions = QHBoxLayout()
        actions.setSpacing(10)
        skip_btn = QPushButton("Skip break")
        skip_btn.setObjectName("skip")
        skip_btn.clicked.connect(self.reject)
        start_btn = QPushButton(f"Start {self.minutes}-min break ->")
        start_btn.setObjectName("start")
        start_btn.clicked.connect(self.accept)
        actions.addWidget(skip_btn)
        actions.addStretch()
        actions.addWidget(start_btn)
        root.addLayout(actions)

    def _label(self, text, klass):
        lbl = QLabel(str(text))
        lbl.setProperty("class", klass)
        return lbl

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
        return (
            f"{best_minutes:.1f} min "
            f"<span style='color:#15803d;'>↑ +{diff:.1f} min</span> "
            f"avg {avg_minutes:.1f} min"
        )
