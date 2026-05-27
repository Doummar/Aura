import json
import math
import os

from PyQt6.QtCore import QPoint, Qt, QTimer, QUrl
from PyQt6.QtWidgets import QApplication, QHBoxLayout, QWidget
from aqt import mw
from aqt.webview import AnkiWebView

from ..core.progress_engine import ProgressEngine
from .break_prompt_dialog import BreakPromptDialog


class HUDOverlay(QWidget):
    TIME_HIT_WIDTH = 100
    DRAG_THRESHOLD = 6

    def __init__(self, manager, config):
        super().__init__(None)
        self.manager = manager
        self.config = config
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        layout = QHBoxLayout()
        layout.setContentsMargins(12, 4, 12, 4)
        self.setLayout(layout)

        self.web_view = AnkiWebView()
        self.web_view.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.web_view.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.web_view.page().setBackgroundColor(Qt.GlobalColor.transparent)
        layout.addWidget(self.web_view)

        self.setFixedSize(320, 40)
        self._press_global = None
        self._drag_offset = QPoint()
        self._press_was_time = False
        self._has_moved = False
        self._prompt_active = False

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(1000)

        self.load_page()
        self.apply_styles()
        self.hide()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            local = event.position().toPoint()
            self._press_global = event.globalPosition().toPoint()
            self._drag_offset = self._press_global - self.pos()
            self._press_was_time = local.x() <= self.TIME_HIT_WIDTH
            self._has_moved = False
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._press_global is not None and (event.buttons() & Qt.MouseButton.LeftButton):
            global_pos = event.globalPosition().toPoint()
            if (global_pos - self._press_global).manhattanLength() >= self.DRAG_THRESHOLD:
                self._has_moved = True
                if not self._press_was_time:
                    self.move(global_pos - self._drag_offset)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._press_global is not None:
            if self._press_was_time and not self._has_moved:
                self.toggle_pause()
            self.config.set('pos', [self.x(), self.y()])
            self._press_global = None
            self._press_was_time = False
            self._has_moved = False
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def toggle_pause(self):
        if not self.manager.is_active:
            return
        self.manager.toggle_pause()
        self.refresh()

    def apply_styles(self):
        self.setWindowOpacity(1.0)
        pos = self.config.get('pos', [50, 50])
        self.move(int(pos[0]), int(pos[1]))

        if self.config.get('show_hud', True):
            if self.manager.is_active:
                self.show()
        else:
            self.hide()

    def load_page(self):
        path = os.path.join(os.path.dirname(__file__), 'web', 'index.html')
        with open(path, encoding='utf-8') as handle:
            html = handle.read()
        self.web_view.setHtml(html, QUrl.fromLocalFile(path))

    def _handle_transition_prompt(self, prompt_type):
        from aqt.utils import askUser

        if prompt_type == 'ASK_BREAK':
            details = self.manager.get_pending_break_details() or {}
            kind = str(details.get('kind', 'SHORT')).upper()
            mins = max(1, int(math.ceil(float(details.get('duration_sec', 60)) / 60.0)))
            dialog = BreakPromptDialog(kind=kind, minutes=mins, details=details, parent=mw)
            if dialog.exec():
                self.manager.respond_to_break_offer(True)
            else:
                self.manager.respond_to_break_offer(False)
            return

        if prompt_type == 'ASK_STUDY':
            return_now = askUser('Break finished. Return to study now?', title='Aura: Study Time')
            self.manager.respond_to_study_offer(return_now)

    def refresh(self):
        try:
            if not self.manager.is_active or not self.isVisible():
                return

            score = self.manager.calculate_cognitive_score()
            self.manager.record_score_sample(score)
            rem = ProgressEngine.get_remaining()
            phase, phase_rem, total_sec, _triggered, is_paused, break_kind, prompt_type = self.manager.get_phase_info()

            if prompt_type and not is_paused and not self._prompt_active:
                self._prompt_active = True
                try:
                    self._handle_transition_prompt(prompt_type)
                finally:
                    self._prompt_active = False
                phase, phase_rem, total_sec, _triggered, is_paused, break_kind, prompt_type = self.manager.get_phase_info()

            payload = json.dumps(
                {
                    'sec': phase_rem,
                    'pct': score,
                    'rem': rem,
                    'phase': phase,
                    'break_kind': break_kind,
                    'total_sec': total_sec,
                    'paused': is_paused,
                    'is_dark': self._is_dark_theme(),
                }
            )
            self.web_view.eval(f'update({payload})')
        except Exception as exc:
            print(f'HUD Refresh Error: {exc}')

    def _is_dark_theme(self):
        try:
            palette = QApplication.palette()
            return palette.window().color().lightness() < 128
        except Exception:
            return False
