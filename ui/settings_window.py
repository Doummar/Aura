from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QSpinBox,
    QVBoxLayout,
)


class SettingsWindow(QDialog):
    MODE_ITEMS = (
        ("Aura HUD", "aura"),
        ("Pomodoro only", "pomodoro"),
        ("Custom", "custom"),
    )

    def __init__(self, config, parent):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Aura - Settings")
        self.setMinimumWidth(540)
        self.setStyleSheet(
            """
            QDialog { background: #f7f7f7; }
            QLabel { color: #111111; font-size: 12px; font-family: "Segoe UI"; }
            QLabel#title { font-size: 17px; font-weight: 700; color: #0f0f0f; }
            QLabel#hint { color: #202020; border: 1px solid #d8d8d8; border-radius: 6px; padding: 8px; background: #ffffff; font-size: 12px; }
            QFrame#sep { background: #dddddd; min-height: 1px; max-height: 1px; border: none; }

            QSlider::groove:horizontal { border: 1px solid #d4d4d4; height: 6px; background: #ececec; border-radius: 3px; }
            QSlider::handle:horizontal { background: #2e6de0; border: none; width: 14px; height: 14px; margin: -5px 0; border-radius: 7px; }

            QSpinBox, QComboBox { padding: 4px 8px; border: 1px solid #d2d2d2; border-radius: 5px; background: #ffffff; min-width: 64px; color: #1f1f1f; }
            QCheckBox { color: #111111; font-size: 12px; spacing: 8px; font-family: "Segoe UI"; }

            QPushButton[class="util"] { background: #ffffff; border: 1px solid #d4d4d4; color: #1f1f1f; border-radius: 5px; padding: 8px; }
            QPushButton[class="util"]:hover { background: #f1f1f1; border-color: #bbbbbb; }

            QPushButton#save-btn { background: #2e6de0; color: #ffffff; border: none; border-radius: 5px; padding: 6px 18px; font-weight: 700; }
            QPushButton#cancel-btn { background: #ffffff; color: #222222; border: 1px solid #d2d2d2; border-radius: 5px; padding: 6px 18px; }
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 16, 22, 16)
        layout.setSpacing(7)

        title = QLabel("Aura: Minimal HUD")
        title.setObjectName("title")
        layout.addWidget(title)

        subtitle = QLabel("Simple and stable controls for study flow.")
        subtitle.setStyleSheet("color:#2b2b2b; font-size:12px;")
        layout.addWidget(subtitle)
        layout.addWidget(self._line())

        layout.addWidget(self._section("MODE"))
        mode_row = QHBoxLayout()
        mode_row.addWidget(QLabel("Mode"))
        mode_row.addStretch()
        self.mode_combo = QComboBox()
        for label, mode in self.MODE_ITEMS:
            self.mode_combo.addItem(label, mode)
        mode = str(config.get("display_mode", "aura")).lower()
        mode_index = self.mode_combo.findData(mode)
        self.mode_combo.setCurrentIndex(mode_index if mode_index >= 0 else 0)
        self.mode_combo.currentIndexChanged.connect(self.apply_mode_to_controls)
        mode_row.addWidget(self.mode_combo)
        layout.addLayout(mode_row)

        self.focus_widgets = []
        focus_section = self._section("FOCUS SCORE")
        self.focus_widgets.append(focus_section)
        layout.addWidget(focus_section)
        sens_row = QHBoxLayout()
        sens_label = QLabel("Sensitivity")
        self.focus_widgets.append(sens_label)
        sens_row.addWidget(sens_label)
        sens_row.addStretch()
        initial_sens = int(float(config.get("sensitivity", 0.5)) * 100)
        initial_sens = max(0, min(100, initial_sens))
        self.sens_val_label = QLabel(f"{initial_sens}%")
        self.sens_val_label.setStyleSheet("font-weight:700;color:#1a4eb6;font-size:13px;")
        self.focus_widgets.append(self.sens_val_label)
        sens_row.addWidget(self.sens_val_label)
        layout.addLayout(sens_row)

        self.sens_slider = QSlider(Qt.Orientation.Horizontal)
        self.sens_slider.setRange(0, 100)
        self.sens_slider.setValue(initial_sens)
        self.sens_slider.valueChanged.connect(self.update_sens_label)
        self.focus_widgets.append(self.sens_slider)
        layout.addWidget(self.sens_slider)

        calibration_row = QHBoxLayout()
        calibration_label = QLabel("Score calibration cards")
        self.focus_widgets.append(calibration_label)
        calibration_row.addWidget(calibration_label)
        calibration_row.addStretch()
        self.calibration_spin = QSpinBox()
        self.calibration_spin.setRange(3, 20)
        self.calibration_spin.setValue(int(config.get("calibration_cards", 5)))
        self.focus_widgets.append(self.calibration_spin)
        calibration_row.addWidget(self.calibration_spin)
        layout.addLayout(calibration_row)

        layout.addWidget(self._section("TIMING"))
        timing = QHBoxLayout()
        timing.setSpacing(18)
        study_box = QVBoxLayout()
        study_box.addWidget(QLabel("Study (min)"))
        self.study_spin = QSpinBox()
        self.study_spin.setRange(1, 120)
        self.study_spin.setValue(int(config.get("study_min", 20)))
        study_box.addWidget(self.study_spin)
        break_box = QVBoxLayout()
        break_box.addWidget(QLabel("Break (min)"))
        self.break_spin = QSpinBox()
        self.break_spin.setRange(1, 60)
        self.break_spin.setValue(int(config.get("break_min", 5)))
        break_box.addWidget(self.break_spin)
        long_break_box = QVBoxLayout()
        long_break_box.addWidget(QLabel("Long break (min)"))
        self.long_break_spin = QSpinBox()
        self.long_break_spin.setRange(1, 180)
        self.long_break_spin.setValue(int(config.get("long_break_min", 15)))
        long_break_box.addWidget(self.long_break_spin)
        timing.addLayout(study_box)
        timing.addLayout(break_box)
        timing.addLayout(long_break_box)
        timing.addStretch()
        layout.addLayout(timing)

        long_every_row = QHBoxLayout()
        long_every_row.addWidget(QLabel("Long break every N breaks"))
        long_every_row.addStretch()
        self.long_break_every_spin = QSpinBox()
        self.long_break_every_spin.setRange(1, 20)
        self.long_break_every_spin.setValue(int(config.get("long_break_every", 4)))
        long_every_row.addWidget(self.long_break_every_spin)
        layout.addLayout(long_every_row)

        layout.addWidget(self._section("HUD"))
        self.hud_check = QCheckBox("Show HUD overlay during reviews")
        self.hud_check.setChecked(bool(config.get("show_hud", True)))
        layout.addWidget(self.hud_check)

        layout.addWidget(self._section("DISPLAY"))
        self.focus_score_check = QCheckBox("Show focus score")
        self.focus_score_check.setChecked(bool(config.get("show_focus_score", True)))
        self.focus_score_check.stateChanged.connect(self.apply_mode_to_controls)
        layout.addWidget(self.focus_score_check)

        self.cards_left_check = QCheckBox("Show cards left")
        self.cards_left_check.setChecked(bool(config.get("show_cards_left", True)))
        layout.addWidget(self.cards_left_check)

        self.progress_bar_check = QCheckBox("Show progress bar")
        self.progress_bar_check.setChecked(bool(config.get("show_progress_bar", True)))
        layout.addWidget(self.progress_bar_check)

        self.summary_check = QCheckBox("Show session summary when review ends")
        self.summary_check.setChecked(bool(config.get("show_session_summary", True)))
        layout.addWidget(self.summary_check)

        pause_hint = QLabel("Pause control: click the time text on the HUD to pause/resume.")
        pause_hint.setObjectName("hint")
        pause_hint.setWordWrap(True)
        layout.addWidget(pause_hint)

        layout.addWidget(self._section("HELP"))
        help_btn = QPushButton("Open Help Guide")
        help_btn.setProperty("class", "util")
        help_btn.clicked.connect(self.open_help_guide)
        layout.addWidget(help_btn)

        issue_btn = QPushButton("Report an Issue")
        issue_btn.setProperty("class", "util")
        issue_btn.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl("https://github.com/Doummar/Aura/issues"))
        )
        layout.addWidget(issue_btn)

        reset_btn = QPushButton("Reset to Default")
        reset_btn.setProperty("class", "util")
        reset_btn.clicked.connect(self.reset_defaults)
        layout.addWidget(reset_btn)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        save_btn = buttons.button(QDialogButtonBox.StandardButton.Save)
        if save_btn:
            save_btn.setObjectName("save-btn")
        cancel_btn = buttons.button(QDialogButtonBox.StandardButton.Cancel)
        if cancel_btn:
            cancel_btn.setObjectName("cancel-btn")
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.apply_mode_to_controls()

    def _line(self):
        line = QFrame()
        line.setObjectName("sep")
        line.setFrameShape(QFrame.Shape.HLine)
        return line

    def _section(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet(
            "font-size:13px; font-weight:700; color:#303030; letter-spacing:0.2px; "
            "margin-top:4px; margin-bottom:2px;"
        )
        return lbl

    def open_help_guide(self):
        self.done(0)
        from aqt import mw
        if hasattr(mw, "aura_v5_active"):
            from .help_window import HelpWindow
            diag = HelpWindow(mw)
            diag.exec()

    def reset_defaults(self):
        index = self.mode_combo.findData("aura")
        self.mode_combo.setCurrentIndex(index if index >= 0 else 0)
        self.sens_slider.setValue(50)
        self.update_sens_label(50)
        self.study_spin.setValue(20)
        self.break_spin.setValue(5)
        self.long_break_spin.setValue(15)
        self.long_break_every_spin.setValue(4)
        self.hud_check.setChecked(True)
        self.focus_score_check.setChecked(True)
        self.cards_left_check.setChecked(True)
        self.progress_bar_check.setChecked(True)
        self.summary_check.setChecked(True)
        self.calibration_spin.setValue(5)
        self.apply_mode_to_controls()

    def update_sens_label(self, val):
        self.sens_val_label.setText(f"{int(val)}%")

    def apply_mode_to_controls(self, *_args):
        mode = self.mode_combo.currentData() or "aura"
        custom = mode == "custom"
        if mode == "aura":
            self.focus_score_check.setChecked(True)
            self.cards_left_check.setChecked(True)
            self.progress_bar_check.setChecked(True)
        elif mode == "pomodoro":
            self.focus_score_check.setChecked(False)
            self.cards_left_check.setChecked(False)
            self.progress_bar_check.setChecked(False)

        for widget in (self.focus_score_check, self.cards_left_check, self.progress_bar_check):
            widget.setEnabled(custom)

        show_focus_settings = bool(self.focus_score_check.isChecked())
        for widget in self.focus_widgets:
            widget.setVisible(show_focus_settings)

    def save(self):
        mode = self.mode_combo.currentData() or "aura"
        self.config.set("display_mode", mode)
        self.config.set("sensitivity", self.sens_slider.value() / 100.0)
        self.config.set("study_min", self.study_spin.value())
        self.config.set("break_min", self.break_spin.value())
        self.config.set("long_break_min", self.long_break_spin.value())
        self.config.set("long_break_every", self.long_break_every_spin.value())
        self.config.set("show_hud", self.hud_check.isChecked())
        self.config.set("show_focus_score", self.focus_score_check.isChecked())
        self.config.set("show_cards_left", self.cards_left_check.isChecked())
        self.config.set("show_progress_bar", self.progress_bar_check.isChecked())
        self.config.set("show_session_summary", self.summary_check.isChecked())
        self.config.set("calibration_cards", self.calibration_spin.value())
        self.accept()
