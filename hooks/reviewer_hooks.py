import time

from aqt import gui_hooks, mw

from ..ui.session_summary_dialog import SessionSummaryDialog


class ReviewerHooks:
    def __init__(self, manager, overlay):
        self.manager = manager
        self.overlay = overlay
        self._installed = False

    def setup(self):
        if self._installed:
            return
        gui_hooks.reviewer_did_show_question.append(self.on_show)
        gui_hooks.reviewer_did_answer_card.append(self.on_answer)
        gui_hooks.reviewer_will_end.append(self.on_end)
        self._installed = True

    def teardown(self):
        if not self._installed:
            return
        for hook, fn in (
            (gui_hooks.reviewer_did_show_question, self.on_show),
            (gui_hooks.reviewer_did_answer_card, self.on_answer),
            (gui_hooks.reviewer_will_end, self.on_end),
        ):
            try:
                hook.remove(fn)
            except ValueError:
                pass
        self._installed = False

    def on_show(self, reviewer):
        if not self.manager.is_active:
            self.manager.start()
            self.overlay.apply_styles()

    def on_answer(self, reviewer, card, ease):
        try:
            if hasattr(reviewer, "_timerStarted"):
                taken = time.time() - reviewer._timerStarted
            else:
                taken = 2.0

            if taken <= 0:
                taken = 1.5
            if taken > 60:
                taken = 60
        except Exception:
            taken = 2.0

        self.manager.card_answered(taken, ease)

    def on_end(self):
        summary = self.manager.get_session_summary()
        show_summary = bool(self.manager.config.get("show_session_summary", True))
        review_finished = self._is_review_finished()
        self.manager.stop()
        self.overlay.hide()
        if show_summary and review_finished and summary:
            summary["show_focus_stats"] = bool(self.manager.config.get("show_focus_score", True)) or bool(
                self.manager.config.get("show_progress_bar", True)
            )
            summary["show_cards_stats"] = bool(self.manager.config.get("show_cards_left", True))
            dlg = SessionSummaryDialog(summary, mw)
            dlg.exec()

    def _is_review_finished(self):
        """True only when reviewer ended because no cards are left."""
        try:
            if mw is None or mw.col is None:
                return False
            sched = mw.col.sched
            if sched is None or not hasattr(sched, "counts"):
                return False
            counts = sched.counts()
            if not isinstance(counts, (tuple, list)) or len(counts) < 3:
                return False
            remaining = int(counts[0]) + int(counts[1]) + int(counts[2])
            return remaining <= 0
        except Exception:
            return False
