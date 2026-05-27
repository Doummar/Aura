from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QSpinBox,
    QVBoxLayout,
)

from .help_window import HelpWindow


class SettingsWindow(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config

        self.setWindowTitle('Aura - Settings')
        self.setMinimumWidth(470)
        self.setStyleSheet(
            """
            QDialog { background: #f5f5f5; }
            QLabel { color: #111111; font-size: 12px; font-family: 'Segoe UI'; }
            QLabel#title { font-size: 34px; font-weight: 700; color: #111111; }
            QLabel.section { font-size: 13px; font-weight: 700; color: #202020; }
            QFrame#sep { background: #dddddd; min-height: 1px; max-height: 1px; border: none; }
            QSpinBox, QLineEdit {
                background: #ffffff; color: #111111; border: 1px solid #d0d0d0;
                border-radius: 6px; min-height: 28px; padding: 2px 8px;
            }
            QPushButton.tool {
                background: #ffffff; color: #111111; border: 1px solid #d0d0d0;
                border-radius: 6px; min-height: 34px;
            }
            QPushButton#save { background: #2e6de0; color: #ffffff; border: none; border-radius: 6px; min-height: 34px; padding: 0 14px; font-weight: 700; }
            QPushButton#cancel { background: #ffffff; color: #111111; border: 1px solid #d0d0d0; border-radius: 6px; min-height: 34px; padding: 0 14px; }
            """
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(8)

        root.addWidget(QLabel('Aura: Minimal HUD', objectName='title'))
        subtitle = QLabel('Simple and stable controls for study flow.')
        subtitle.setWordWrap(True)
        root.addWidget(subtitle)
        root.addWidget(self._line())

        root.addWidget(self._section('COGNITIVE'))
        sens_row = QHBoxLayout()
        sens_row.addWidget(QLabel('Sensitivity'))
        self.sensitivity_label = QLabel('50%')
        self.sensitivity_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        sens_row.addWidget(self.sensitivity_label)
        root.addLayout(sens_row)

        self.sensitivity_slider = QSlider(Qt.Orientation.Horizontal)
        self.sensitivity_slider.setMinimum(0)
        self.sensitivity_slider.setMaximum(100)
        self.sensitivity_slider.setValue(int(float(config.get('sensitivity', 0.5)) * 100.0))
        self.sensitivity_slider.valueChanged.connect(self._update_sens_label)
        root.addWidget(self.sensitivity_slider)

        cal_row = QHBoxLayout()
        cal_row.addWidget(QLabel('Score calibration cards'))
        self.calibration_spin = QSpinBox()
        self.calibration_spin.setRange(3, 20)
        self.calibration_spin.setValue(int(config.get('calibration_cards', 5)))
        cal_row.addWidget(self.calibration_spin)
        root.addLayout(cal_row)

        root.addWidget(self._line())
        root.addWidget(self._section('TIMING'))

        timing_row = QHBoxLayout()
        study_box = QVBoxLayout()
        study_box.addWidget(QLabel('Study (min)'))
        self.study_spin = QSpinBox()
        self.study_spin.setRange(1, 120)
        self.study_spin.setValue(int(config.get('study_min', 20)))
        study_box.addWidget(self.study_spin)
        timing_row.addLayout(study_box)

        break_box = QVBoxLayout()
        break_box.addWidget(QLabel('Break (min)'))
        self.break_spin = QSpinBox()
        self.break_spin.setRange(1, 60)
        self.break_spin.setValue(int(config.get('break_min', 5)))
        break_box.addWidget(self.break_spin)
        timing_row.addLayout(break_box)

        root.addLayout(timing_row)

        long_row = QHBoxLayout()
        long_box = QVBoxLayout()
        long_box.addWidget(QLabel('Long break (min)'))
        self.long_break_spin = QSpinBox()
        self.long_break_spin.setRange(1, 180)
        self.long_break_spin.setValue(int(config.get('long_break_min', 15)))
        long_box.addWidget(self.long_break_spin)
        long_row.addLayout(long_box)

        every_box = QVBoxLayout()
        every_box.addWidget(QLabel('Long break every N breaks'))
        self.long_break_every_spin = QSpinBox()
        self.long_break_every_spin.setRange(1, 20)
        self.long_break_every_spin.setValue(int(config.get('long_break_every', 4)))
        every_box.addWidget(self.long_break_every_spin)
        long_row.addLayout(every_box)

        root.addLayout(long_row)

        root.addWidget(self._line())
        root.addWidget(self._section('HUD'))

        self.show_hud_check = QCheckBox('Show HUD overlay during reviews')
        self.show_hud_check.setChecked(bool(config.get('show_hud', True)))
        root.addWidget(self.show_hud_check)

        self.summary_check = QCheckBox('Show session summary when review ends')
        self.summary_check.setChecked(bool(config.get('show_session_summary', True)))
        root.addWidget(self.summary_check)

        note = QLabel('Pause control: click the time text on the HUD to pause/resume.')
        note.setWordWrap(True)
        note.setStyleSheet('background:#ffffff; border:1px solid #d0d0d0; border-radius:6px; padding:7px 10px;')
        root.addWidget(note)

        root.addWidget(self._line())
        root.addWidget(self._section('HELP'))

        help_btn = QPushButton('Open Help Guide')
        help_btn.setProperty('class', 'tool')
        help_btn.setObjectName('open-help')
        help_btn.clicked.connect(self._open_help)
        root.addWidget(help_btn)

        issue_btn = QPushButton('Report an Issue')
        issue_btn.setProperty('class', 'tool')
        issue_btn.clicked.connect(self._open_issues)
        root.addWidget(issue_btn)

        reset_btn = QPushButton('Reset to Default')
        reset_btn.setProperty('class', 'tool')
        reset_btn.clicked.connect(self._reset_defaults)
        root.addWidget(reset_btn)

        actions = QHBoxLayout()
        actions.addStretch()
        save_btn = QPushButton('Save')
        save_btn.setObjectName('save')
        save_btn.clicked.connect(self._save)
        cancel_btn = QPushButton('Cancel')
        cancel_btn.setObjectName('cancel')
        cancel_btn.clicked.connect(self.reject)
        actions.addWidget(save_btn)
        actions.addWidget(cancel_btn)
        root.addLayout(actions)

        self._update_sens_label(self.sensitivity_slider.value())

    def _line(self):
        line = QFrame()
        line.setObjectName('sep')
        line.setFrameShape(QFrame.Shape.HLine)
        return line

    def _section(self, text):
        lbl = QLabel(text)
        lbl.setProperty('class', 'section')
        return lbl

    def _update_sens_label(self, value):
        self.sensitivity_label.setText(f'{int(value)}%')

    def _open_help(self):
        HelpWindow(self).exec()

    def _open_issues(self):
        from aqt.utils import openLink
        openLink('https://github.com/Doummar/Aura/issues')

    def _reset_defaults(self):
        self.sensitivity_slider.setValue(50)
        self.calibration_spin.setValue(5)
        self.study_spin.setValue(20)
        self.break_spin.setValue(5)
        self.long_break_spin.setValue(15)
        self.long_break_every_spin.setValue(4)
        self.show_hud_check.setChecked(True)
        self.summary_check.setChecked(True)

    def _save(self):
        self.config.set('sensitivity', self.sensitivity_slider.value() / 100.0)
        self.config.set('calibration_cards', self.calibration_spin.value())
        self.config.set('study_min', self.study_spin.value())
        self.config.set('break_min', self.break_spin.value())
        self.config.set('long_break_min', self.long_break_spin.value())
        self.config.set('long_break_every', self.long_break_every_spin.value())
        self.config.set('show_hud', self.show_hud_check.isChecked())
        self.config.set('show_session_summary', self.summary_check.isChecked())
        self.accept()
