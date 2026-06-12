from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)


class SettingsWindow(QDialog):
    MODE_ITEMS = (
        ("Aura HUD  (timer + rhythm + cards)", "aura"),
        ("Pomodoro only", "pomodoro"),
        ("Custom", "custom"),
    )

    def __init__(self, config, parent):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Aura Settings")
        self.setMinimumWidth(440)
        self.resize(460, 490)

        # ── Styling: close to native Anki/Qt, minimal overrides ──────────
        self.setStyleSheet("""
            QTabBar::tab {
                padding: 5px 20px;
                border: 1px solid #c0c0c0;
                border-bottom: none;
                border-radius: 3px 3px 0 0;
                background: #ebebeb;
                margin-right: 2px;
                font-size: 12px;
            }
            QTabBar::tab:selected {
                background: #2e6de0;
                color: #ffffff;
                border-color: #2e6de0;
            }
            QTabBar::tab:hover:!selected { background: #dcdcdc; }
            QTabWidget::pane {
                border: 1px solid #c0c0c0;
                padding: 6px;
                background: #f6f6f6;
            }
            QGroupBox {
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                margin-top: 10px;
                padding: 10px 8px 8px 8px;
                background: #f6f6f6;
                font-size: 12px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 8px;
                top: 0px;
                padding: 0 4px;
                color: #303030;
            }
            QLabel   { font-size: 12px; color: #111; }
            QCheckBox { font-size: 12px; spacing: 6px; }
            QSpinBox, QComboBox {
                padding: 3px 6px;
                border: 1px solid #c0c0c0;
                border-radius: 3px;
                background: #ffffff;
                min-width: 90px;
                font-size: 12px;
            }
            QSlider::groove:horizontal {
                height: 5px;
                background: #dcdcdc;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #2e6de0;
                width: 13px;
                height: 13px;
                margin: -4px 0;
                border-radius: 7px;
                border: none;
            }
            QPushButton {
                padding: 5px 14px;
                border: 1px solid #c0c0c0;
                border-radius: 3px;
                background: #f0f0f0;
                font-size: 12px;
            }
            QPushButton:hover { background: #e2e2e2; }
            QPushButton#save-btn {
                background: #2e6de0;
                color: #ffffff;
                border: none;
                font-weight: bold;
                padding: 5px 20px;
            }
            QPushButton#save-btn:hover { background: #2558c4; }
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(8)

        # ── Tab widget ────────────────────────────────────────────────────
        self.tabs = QTabWidget()
        self.focus_widgets = []   # populated in _build_rhythm_tab

        # Build tabs — signal connections happen AFTER all widgets exist
        self.tabs.addTab(self._build_timer_tab(),   "Timer")
        self.tabs.addTab(self._build_display_tab(), "Display")
        self.tabs.addTab(self._build_rhythm_tab(),  "Rhythm")
        self.tabs.addTab(self._build_help_tab(),    "Help")

        root.addWidget(self.tabs, 1)

        # ── Save / Cancel ─────────────────────────────────────────────────
        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )
        save_btn = btns.button(QDialogButtonBox.StandardButton.Save)
        if save_btn:
            save_btn.setObjectName("save-btn")
        btns.accepted.connect(self.save)
        btns.rejected.connect(self.reject)
        root.addWidget(btns)

        # ── Connect signals after all widgets are built ───────────────────
        self.mode_combo.currentIndexChanged.connect(self.apply_mode_to_controls)
        self.focus_score_check.stateChanged.connect(self.apply_mode_to_controls)
        self.progress_bar_check.stateChanged.connect(self.apply_mode_to_controls)

        self.apply_mode_to_controls()

    # ─────────────────────────────────────────────────────────────────────
    # Tab builders
    # ─────────────────────────────────────────────────────────────────────

    def _build_timer_tab(self):
        tab = QWidget()
        v = QVBoxLayout(tab)
        v.setSpacing(8)
        v.setContentsMargins(4, 4, 4, 4)

        # Mode ─────────────────────────────────────────────────────────────
        mode_group = QGroupBox("Mode")
        mode_form = QFormLayout(mode_group)
        mode_form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)
        mode_form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        self.mode_combo = QComboBox()
        for label, data in self.MODE_ITEMS:
            self.mode_combo.addItem(label, data)
        saved_mode = str(self.config.get("display_mode", "aura")).lower()
        idx = self.mode_combo.findData(saved_mode)
        self.mode_combo.setCurrentIndex(idx if idx >= 0 else 0)
        mode_form.addRow("Display mode", self.mode_combo)
        v.addWidget(mode_group)

        # Durations ────────────────────────────────────────────────────────
        dur_group = QGroupBox("Durations")
        dur_form = QFormLayout(dur_group)
        dur_form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)
        dur_form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        self.study_spin = QSpinBox()
        self.study_spin.setRange(1, 120)
        self.study_spin.setSuffix(" min")
        self.study_spin.setValue(int(self.config.get("study_min", 20)))
        dur_form.addRow("Study duration", self.study_spin)

        self.break_spin = QSpinBox()
        self.break_spin.setRange(1, 60)
        self.break_spin.setSuffix(" min")
        self.break_spin.setValue(int(self.config.get("break_min", 5)))
        dur_form.addRow("Short break", self.break_spin)

        self.long_break_spin = QSpinBox()
        self.long_break_spin.setRange(1, 180)
        self.long_break_spin.setSuffix(" min")
        self.long_break_spin.setValue(int(self.config.get("long_break_min", 15)))
        dur_form.addRow("Long break", self.long_break_spin)

        self.long_break_every_spin = QSpinBox()
        self.long_break_every_spin.setRange(1, 20)
        self.long_break_every_spin.setValue(int(self.config.get("long_break_every", 4)))
        dur_form.addRow("Sessions before long break", self.long_break_every_spin)

        v.addWidget(dur_group)

        # Options ──────────────────────────────────────────────────────────
        opt_group = QGroupBox("Options")
        opt_v = QVBoxLayout(opt_group)
        self.continue_check = QCheckBox("Continue timer across decks")
        self.continue_check.setChecked(bool(self.config.get("continue_across_decks", False)))
        opt_v.addWidget(self.continue_check)

        # Sub-option: what to do with the timer between decks
        cross_row = QHBoxLayout()
        cross_row.setContentsMargins(22, 0, 0, 0)
        self.cross_deck_label = QLabel("Between decks:")
        cross_row.addWidget(self.cross_deck_label)
        self.cross_deck_combo = QComboBox()
        self.cross_deck_combo.addItem("Pause timer", "pause")
        self.cross_deck_combo.addItem("Keep running", "continue")
        saved_cd = str(self.config.get("cross_deck_behavior", "continue"))
        self.cross_deck_combo.setCurrentIndex(
            0 if saved_cd == "pause" else 1
        )
        cross_row.addWidget(self.cross_deck_combo)
        cross_row.addStretch()
        opt_v.addLayout(cross_row)

        # Enable sub-combo only when continue is checked
        self.continue_check.stateChanged.connect(self._update_cross_deck_controls)
        self._update_cross_deck_controls()

        v.addWidget(opt_group)

        v.addStretch()
        return tab

    def _build_display_tab(self):
        tab = QWidget()
        v = QVBoxLayout(tab)
        v.setSpacing(8)
        v.setContentsMargins(4, 4, 4, 4)

        # HUD ──────────────────────────────────────────────────────────────
        hud_group = QGroupBox("HUD")
        hud_v = QVBoxLayout(hud_group)
        self.hud_check = QCheckBox("Show HUD overlay during reviews")
        self.hud_check.setChecked(bool(self.config.get("show_hud", True)))
        hud_v.addWidget(self.hud_check)
        v.addWidget(hud_group)

        # Elements ─────────────────────────────────────────────────────────
        elem_group = QGroupBox("Elements")
        elem_v = QVBoxLayout(elem_group)

        self.focus_score_check = QCheckBox("Show focus rhythm %")
        self.focus_score_check.setChecked(bool(self.config.get("show_focus_score", True)))
        elem_v.addWidget(self.focus_score_check)

        self.cards_left_check = QCheckBox("Show cards left")
        self.cards_left_check.setChecked(bool(self.config.get("show_cards_left", True)))
        elem_v.addWidget(self.cards_left_check)

        # Rhythm bar row: [✓ Show rhythm bar] ··· [Dot ▾]
        bar_row = QHBoxLayout()
        self.progress_bar_check = QCheckBox("Show rhythm bar")
        self.progress_bar_check.setChecked(bool(self.config.get("show_progress_bar", True)))
        bar_row.addWidget(self.progress_bar_check)
        bar_row.addStretch()
        self.bar_style_combo = QComboBox()
        self.bar_style_combo.addItem("Dot", "dot")
        self.bar_style_combo.addItem("Bar", "bar")
        current_style = str(self.config.get("progress_bar_style", "bar")).lower()
        self.bar_style_combo.setCurrentIndex(1 if current_style == "bar" else 0)
        bar_row.addWidget(self.bar_style_combo)
        elem_v.addLayout(bar_row)

        v.addWidget(elem_group)

        # Session summary ──────────────────────────────────────────────────
        sum_group = QGroupBox("Session Summary")
        sum_v = QVBoxLayout(sum_group)
        self.summary_check = QCheckBox("Show summary when review ends")
        self.summary_check.setChecked(bool(self.config.get("show_session_summary", True)))
        sum_v.addWidget(self.summary_check)
        v.addWidget(sum_group)

        v.addStretch()
        return tab

    def _build_rhythm_tab(self):
        tab = QWidget()
        v = QVBoxLayout(tab)
        v.setSpacing(8)
        v.setContentsMargins(4, 4, 4, 4)

        # ── Answer Weights ─────────────────────────────────────────────────
        weights_group = QGroupBox("Answer Weights")
        wg_v = QVBoxLayout(weights_group)
        wg_v.setSpacing(3)

        for btn_label, config_key, default in [
            ("Again", "weight_again", -2),
            ("Hard",  "weight_hard",  -1),
            ("Good",  "weight_good",   1),
            ("Easy",  "weight_easy",   0),
        ]:
            saved = max(-2, min(2, int(self.config.get(config_key, default))))
            row = QHBoxLayout()

            lbl = QLabel(btn_label)
            lbl.setFixedWidth(42)
            self.focus_widgets.append(lbl)
            row.addWidget(lbl)

            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(-2, 2)
            slider.setValue(saved)
            self.focus_widgets.append(slider)
            row.addWidget(slider)

            val_lbl = QLabel(self._fmt_weight(saved))
            val_lbl.setFixedWidth(28)
            val_lbl.setAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
            val_lbl.setStyleSheet("font-weight: bold; color: #2e6de0; font-size: 12px;")
            slider.valueChanged.connect(
                lambda val, l=val_lbl: l.setText(self._fmt_weight(val))
            )
            self.focus_widgets.append(val_lbl)
            row.addWidget(val_lbl)

            setattr(self, f"{config_key}_slider", slider)
            wg_v.addLayout(row)

        wg_v.addSpacing(4)
        reset_w_btn = QPushButton("Reset weights")
        reset_w_btn.clicked.connect(self.reset_weights)
        self.focus_widgets.append(reset_w_btn)
        wg_v.addWidget(reset_w_btn)
        v.addWidget(weights_group)

        # ── Rhythm Sensitivity ─────────────────────────────────────────────
        sens_group = QGroupBox("Rhythm Sensitivity")
        sg_v = QVBoxLayout(sens_group)
        sg_v.setSpacing(3)

        # Reaction speed
        sens_row = QHBoxLayout()
        sens_lbl = QLabel("Reaction speed")
        self.focus_widgets.append(sens_lbl)
        sens_row.addWidget(sens_lbl)
        sens_row.addStretch()
        initial_sens = max(0, min(100, int(float(self.config.get("sensitivity", 0.5)) * 100)))
        self.sens_val_label = QLabel(f"{initial_sens}%")
        self.sens_val_label.setStyleSheet("font-weight: bold; color: #2e6de0;")
        self.focus_widgets.append(self.sens_val_label)
        sens_row.addWidget(self.sens_val_label)
        sg_v.addLayout(sens_row)
        self.sens_slider = QSlider(Qt.Orientation.Horizontal)
        self.sens_slider.setRange(0, 100)
        self.sens_slider.setValue(initial_sens)
        self.sens_slider.valueChanged.connect(self.update_sens_label)
        self.focus_widgets.append(self.sens_slider)
        sg_v.addWidget(self.sens_slider)

        sg_v.addSpacing(4)

        # Calibration cards
        cal_form = QFormLayout()
        cal_form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)
        cal_form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        self.calibration_spin = QSpinBox()
        self.calibration_spin.setRange(3, 20)
        self.calibration_spin.setValue(int(self.config.get("calibration_cards", 5)))
        cal_lbl = QLabel("Calibration cards")
        self.focus_widgets.extend([cal_lbl, self.calibration_spin])
        cal_form.addRow(cal_lbl, self.calibration_spin)
        sg_v.addLayout(cal_form)

        sg_v.addSpacing(4)

        # Warning threshold
        thresh_row = QHBoxLayout()
        thresh_lbl = QLabel("Warning threshold")
        self.focus_widgets.append(thresh_lbl)
        thresh_row.addWidget(thresh_lbl)
        thresh_row.addStretch()
        initial_thresh = max(20, min(60, int(self.config.get("warning_threshold", 40))))
        self.thresh_val_label = QLabel(f"{initial_thresh}%")
        self.thresh_val_label.setStyleSheet("font-weight: bold; color: #2e6de0;")
        self.focus_widgets.append(self.thresh_val_label)
        thresh_row.addWidget(self.thresh_val_label)
        sg_v.addLayout(thresh_row)
        self.thresh_slider = QSlider(Qt.Orientation.Horizontal)
        self.thresh_slider.setRange(20, 60)
        self.thresh_slider.setValue(initial_thresh)
        self.thresh_slider.valueChanged.connect(self.update_thresh_label)
        self.focus_widgets.append(self.thresh_slider)
        sg_v.addWidget(self.thresh_slider)

        sg_v.addSpacing(4)

        # Response time weight
        rt_row = QHBoxLayout()
        rt_lbl = QLabel("Response time")
        self.focus_widgets.append(rt_lbl)
        rt_row.addWidget(rt_lbl)
        rt_row.addStretch()
        initial_rt = max(0, min(2, int(self.config.get("response_time_weight", 1))))
        self.rt_val_label = QLabel(self._fmt_rt(initial_rt))
        self.rt_val_label.setStyleSheet("font-weight: bold; color: #2e6de0;")
        self.focus_widgets.append(self.rt_val_label)
        rt_row.addWidget(self.rt_val_label)
        sg_v.addLayout(rt_row)
        self.rt_slider = QSlider(Qt.Orientation.Horizontal)
        self.rt_slider.setRange(0, 2)
        self.rt_slider.setValue(initial_rt)
        self.rt_slider.valueChanged.connect(self.update_rt_label)
        self.focus_widgets.append(self.rt_slider)
        sg_v.addWidget(self.rt_slider)

        sg_v.addSpacing(2)
        self.ignore_easy_time_check = QCheckBox("Ignore Easy answers for response time")
        self.ignore_easy_time_check.setChecked(bool(self.config.get("ignore_easy_time", False)))
        self.focus_widgets.append(self.ignore_easy_time_check)
        sg_v.addWidget(self.ignore_easy_time_check)

        v.addWidget(sens_group)
        v.addStretch()
        return tab

    def _build_help_tab(self):
        tab = QWidget()
        v = QVBoxLayout(tab)
        v.setSpacing(8)
        v.setContentsMargins(4, 4, 4, 4)

        # Resources
        res_group = QGroupBox("Resources")
        res_v = QVBoxLayout(res_group)

        help_btn = QPushButton("Open Help Guide")
        help_btn.clicked.connect(self.open_help_guide)
        res_v.addWidget(help_btn)

        issue_btn = QPushButton("Report an Issue")
        issue_btn.clicked.connect(
            lambda: QDesktopServices.openUrl(
                QUrl("https://github.com/Doummar/Aura/issues")
            )
        )
        res_v.addWidget(issue_btn)
        v.addWidget(res_group)

        # Reset
        reset_group = QGroupBox("Reset")
        reset_v = QVBoxLayout(reset_group)
        reset_btn = QPushButton("Reset to Default")
        reset_btn.clicked.connect(self.reset_defaults)
        reset_v.addWidget(reset_btn)
        v.addWidget(reset_group)

        # Pause hint
        hint_group = QGroupBox("Tips")
        hint_v = QVBoxLayout(hint_group)
        for tip_text in (
            "Click the time on the HUD to pause or resume the timer.",
            "Press and hold the time display for ~0.6 s to reset the timer.",
        ):
            tip = QLabel(tip_text)
            tip.setWordWrap(True)
            tip.setStyleSheet("color: #444;")
            hint_v.addWidget(tip)
        v.addWidget(hint_group)

        v.addStretch()
        return tab

    # ─────────────────────────────────────────────────────────────────────
    # Slots
    # ─────────────────────────────────────────────────────────────────────

    def open_help_guide(self):
        self.done(0)
        from aqt import mw
        if hasattr(mw, "aura_v5_active"):
            from .help_window import HelpWindow
            HelpWindow(mw).exec()

    def reset_defaults(self):
        idx = self.mode_combo.findData("aura")
        self.mode_combo.setCurrentIndex(idx if idx >= 0 else 0)
        self.study_spin.setValue(20)
        self.break_spin.setValue(5)
        self.long_break_spin.setValue(15)
        self.long_break_every_spin.setValue(4)
        self.continue_check.setChecked(False)
        self.cross_deck_combo.setCurrentIndex(1)   # "Keep running"
        self._update_cross_deck_controls()
        self.hud_check.setChecked(True)
        self.focus_score_check.setChecked(True)
        self.cards_left_check.setChecked(True)
        self.progress_bar_check.setChecked(True)
        self.bar_style_combo.setCurrentIndex(1)   # Bar = index 1
        self.summary_check.setChecked(True)
        self.sens_slider.setValue(50)
        self.update_sens_label(50)
        self.calibration_spin.setValue(5)
        self.thresh_slider.setValue(40)
        self.update_thresh_label(40)
        self.reset_weights()
        self.rt_slider.setValue(1)
        self.update_rt_label(1)
        self.ignore_easy_time_check.setChecked(False)
        self.apply_mode_to_controls()

    @staticmethod
    def _fmt_weight(val):
        v = int(val)
        return f"+{v}" if v > 0 else str(v)

    @staticmethod
    def _fmt_rt(val):
        return "Off" if int(val) == 0 else f"×{int(val)}"

    def reset_weights(self):
        self.weight_again_slider.setValue(-2)
        self.weight_hard_slider.setValue(-1)
        self.weight_good_slider.setValue(1)
        self.weight_easy_slider.setValue(0)

    def update_rt_label(self, val):
        self.rt_val_label.setText(self._fmt_rt(val))

    def update_thresh_label(self, val):
        self.thresh_val_label.setText(f"{int(val)}%")

    def update_sens_label(self, val):
        self.sens_val_label.setText(f"{int(val)}%")

    def _update_cross_deck_controls(self):
        enabled = self.continue_check.isChecked()
        self.cross_deck_label.setEnabled(enabled)
        self.cross_deck_combo.setEnabled(enabled)

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

        for w in (self.focus_score_check, self.cards_left_check, self.progress_bar_check):
            w.setEnabled(custom)

        show_rhythm = (
            bool(self.focus_score_check.isChecked()) or
            bool(self.progress_bar_check.isChecked())
        )
        # Dim rhythm tab when it has no effect (pomodoro / custom with all off)
        if not show_rhythm and self.tabs.currentIndex() == 2:
            self.tabs.setCurrentIndex(0)
        self.tabs.setTabEnabled(2, show_rhythm)

        for w in self.focus_widgets:
            w.setEnabled(show_rhythm)

        self.bar_style_combo.setEnabled(bool(self.progress_bar_check.isChecked()))

    def save(self):
        self.config.set("display_mode",          self.mode_combo.currentData() or "aura")
        self.config.set("study_min",             self.study_spin.value())
        self.config.set("break_min",             self.break_spin.value())
        self.config.set("long_break_min",        self.long_break_spin.value())
        self.config.set("long_break_every",      self.long_break_every_spin.value())
        self.config.set("continue_across_decks", self.continue_check.isChecked())
        self.config.set("cross_deck_behavior",   self.cross_deck_combo.currentData() or "continue")
        self.config.set("show_hud",              self.hud_check.isChecked())
        self.config.set("show_focus_score",      self.focus_score_check.isChecked())
        self.config.set("show_cards_left",       self.cards_left_check.isChecked())
        self.config.set("show_progress_bar",     self.progress_bar_check.isChecked())
        self.config.set("progress_bar_style",    self.bar_style_combo.currentData() or "bar")
        self.config.set("show_session_summary",  self.summary_check.isChecked())
        self.config.set("sensitivity",           self.sens_slider.value() / 100.0)
        self.config.set("calibration_cards",     self.calibration_spin.value())
        self.config.set("warning_threshold",     self.thresh_slider.value())
        self.config.set("weight_again",          self.weight_again_slider.value())
        self.config.set("weight_hard",           self.weight_hard_slider.value())
        self.config.set("weight_good",           self.weight_good_slider.value())
        self.config.set("weight_easy",           self.weight_easy_slider.value())
        self.config.set("response_time_weight",  self.rt_slider.value())
        self.config.set("ignore_easy_time",      self.ignore_easy_time_check.isChecked())
        self.accept()
