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
        # Let the overlay widget receive mouse events for drag/pause handling.
        self.web_view.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.web_view.page().setBackgroundColor(Qt.GlobalColor.transparent)
        layout.addWidget(self.web_view)

        self.setFixedSize(320, 40)
        self._press_global = None
        self._drag_offset = QPoint()
        self._press_was_time = False
        self._has_moved = False
        self._long_press_fired = False
        self._prompt_active = False
        self._page_ready = False

        # Press-and-hold the time display to reset the phase timer.
        self._long_press_timer = QTimer(self)
        self._long_press_timer.setSingleShot(True)
        self._long_press_timer.setInterval(650)
        self._long_press_timer.timeout.connect(self._on_long_press)

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
            self._long_press_fired = False
            # Hold on the time display resets the timer.
            if self._press_was_time:
                self._long_press_timer.start()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._press_global is not None and (event.buttons() & Qt.MouseButton.LeftButton):
            global_pos = event.globalPosition().toPoint()
            if (global_pos - self._press_global).manhattanLength() >= self.DRAG_THRESHOLD:
                self._has_moved = True
                # Dragging cancels any pending long-press reset.
                if self._long_press_timer.isActive():
                    self._long_press_timer.stop()
                if not self._press_was_time:
                    self.move(global_pos - self._drag_offset)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._press_global is not None:
            if self._long_press_timer.isActive():
                self._long_press_timer.stop()
            # Single click on time = pause/resume; skip if hold already reset.
            if self._press_was_time and not self._has_moved and not self._long_press_fired:
                self.toggle_pause()
            self.config.set("pos", [self.x(), self.y()])
            self._press_global = None
            self._press_was_time = False
            self._long_press_fired = False
            self._has_moved = False
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def toggle_pause(self):
        if not self.manager.is_active:
            return
        self.manager.toggle_pause()
        self.refresh()

    def _on_long_press(self):
        """Fired when the user holds the time display for 650 ms — resets the timer."""
        if self._has_moved or not self.manager.is_active:
            return
        self._long_press_fired = True
        self.manager.reset_phase()
        self.refresh()

    def apply_styles(self):
        self.setWindowOpacity(1.0)
        pos = self.config.get("pos", [50, 50])
        self.move(int(pos[0]), int(pos[1]))

        if self.config.get("show_hud", True):
            # Only show while a reviewer is actually open. Avoids the overlay
            # leaking onto the deck browser or overview when settings are closed
            # during a cross-deck session (manager stays active between decks).
            if self.manager.is_active and getattr(mw, "state", "") == "review":
                self.show()
        else:
            self.hide()

    def load_page(self):
        self._page_ready = False
        path = os.path.join(os.path.dirname(__file__), "web", "index.html")
        with open(path, encoding="utf-8") as handle:
            html = handle.read()
        self.web_view.page().loadFinished.connect(self._on_page_ready)
        self.web_view.setHtml(html, QUrl.fromLocalFile(path))

    def _on_page_ready(self, ok):
        self._page_ready = bool(ok)

    def _handle_transition_prompt(self, prompt_type):
        from aqt.utils import askUser

        if prompt_type == "ASK_BREAK":
            details = self.manager.get_pending_break_details() or {}
            details["show_focus_stats"] = self._show_focus_stats()
            details["show_cards_stats"] = bool(self.config.get("show_cards_left", True))
            kind = str(details.get("kind", "SHORT")).upper()
            mins = max(1, int(math.ceil(float(details.get("duration_sec", 60)) / 60.0)))
            dialog = BreakPromptDialog(kind=kind, minutes=mins, details=details, parent=mw)
            if dialog.exec():
                self.manager.respond_to_break_offer(True)
            else:
                self.manager.respond_to_break_offer(False)
            return

        if prompt_type == "ASK_STUDY":
            return_now = askUser(
                "Break finished. Return to study now?",
                title="Aura: Study Time",
            )
            self.manager.respond_to_study_offer(return_now)

    def refresh(self):
        try:
            if not self.manager.is_active or not self.isVisible():
                return
            if not self._page_ready:
                return

            show_focus_score = bool(self.config.get("show_focus_score", True))
            show_cards_left = bool(self.config.get("show_cards_left", True))
            show_progress_bar = bool(self.config.get("show_progress_bar", True))
            # BUG FIX: pass bar_style so the HUD can choose dot vs fill bar
            bar_style = str(self.config.get("progress_bar_style", "bar"))

            if show_focus_score or show_progress_bar:
                score = self.manager.calculate_cognitive_score()
                self.manager.record_score_sample(score)
            else:
                score = int(round(self.manager.smoothed_score))

            rem = ProgressEngine.get_remaining()
            phase, phase_rem, total_sec, _triggered, is_paused, break_kind, prompt_type = (
                self.manager.get_phase_info()
            )

            if prompt_type and not is_paused and not self._prompt_active:
                self._prompt_active = True
                try:
                    self._handle_transition_prompt(prompt_type)
                finally:
                    self._prompt_active = False
                phase, phase_rem, total_sec, _triggered, is_paused, break_kind, prompt_type = (
                    self.manager.get_phase_info()
                )

            payload = json.dumps(
                {
                    "sec": phase_rem,
                    "pct": score,
                    "rem": rem,
                    "phase": phase,
                    "break_kind": break_kind,
                    "total_sec": total_sec,
                    "paused": is_paused,
                    "is_dark": self._is_dark_theme(),
                    "show_focus_score": show_focus_score,
                    "show_cards_left": show_cards_left,
                    "show_progress_bar": show_progress_bar,
                    "bar_style": bar_style,
                    "warning_threshold": int(self.config.get("warning_threshold", 40)),
                }
            )
            self.web_view.eval(f"update({payload})")
        except Exception as exc:
            print(f"HUD Refresh Error: {exc}")

    def _is_dark_theme(self):
        try:
            palette = QApplication.palette()
            return palette.window().color().lightness() < 128
        except Exception:
            return False

    def _show_focus_stats(self):
        return bool(self.config.get("show_focus_score", True)) or bool(
            self.config.get("show_progress_bar", True)
        )
