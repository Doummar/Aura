import math
import time


class SessionManager:
    FOCUS_THRESHOLD = 50

    def __init__(self, config):
        self.config = config
        self.start_time = 0.0
        self.cards_studied = 0
        self.again_count = 0
        self.latencies = []
        self.is_active = False
        self.is_paused = False
        self.pause_started_at = 0.0
        self.total_paused_seconds = 0.0
        self.phase = "STUDY"
        self.break_kind = "SHORT"
        self.phase_started_elapsed = 0.0
        self.phase_duration_sec = 0
        self.completed_study_blocks = 0
        self.completed_breaks = 0
        self.completed_long_breaks = 0
        self.total_break_seconds = 0.0

        self.smoothed_score = 50.0
        self.score_samples = []
        self.score_sum = 0.0
        self.score_count = 0
        self.last_score_sample_elapsed = None
        self.current_focus_streak_sec = 0.0
        self.best_focus_streak_sec = 0.0
        self.focus_streak_total_sec = 0.0
        self.focus_streak_count = 0
        self.pending_break_offer = False
        self.pending_return_offer = False
        self.pending_break_kind = "SHORT"
        self.pending_break_duration_sec = 0

    def start(self):
        self.start_time = time.time()
        self.cards_studied = 0
        self.again_count = 0
        self.latencies = []
        self.is_active = True
        self.is_paused = False
        self.pause_started_at = 0.0
        self.total_paused_seconds = 0.0
        self.phase = "STUDY"
        self.break_kind = "SHORT"
        self.completed_study_blocks = 0
        self.completed_breaks = 0
        self.completed_long_breaks = 0
        self.total_break_seconds = 0.0
        self.smoothed_score = 50.0
        self.score_samples = []
        self.score_sum = 0.0
        self.score_count = 0
        self.last_score_sample_elapsed = None
        self.current_focus_streak_sec = 0.0
        self.best_focus_streak_sec = 0.0
        self.focus_streak_total_sec = 0.0
        self.focus_streak_count = 0
        self.pending_break_offer = False
        self.pending_return_offer = False
        self.pending_break_kind = "SHORT"
        self.pending_break_duration_sec = 0
        self._set_phase("STUDY", self._study_sec())

    def stop(self):
        self.is_active = False
        self.is_paused = False
        self.pause_started_at = 0.0
        self.pending_break_offer = False
        self.pending_return_offer = False

    def pause(self):
        if not self.is_active or self.is_paused:
            return False
        self.is_paused = True
        self.pause_started_at = time.time()
        return True

    def resume(self):
        if not self.is_active or not self.is_paused:
            return False
        now = time.time()
        self.total_paused_seconds += max(0.0, now - self.pause_started_at)
        self.pause_started_at = 0.0
        self.is_paused = False
        return True

    def toggle_pause(self):
        if not self.is_active:
            return False
        if self.is_paused:
            self.resume()
        else:
            self.pause()
        return self.is_paused

    def _clamp_int(self, value, default, min_value, max_value):
        try:
            n = int(value)
        except Exception:
            return default
        return max(min_value, min(max_value, n))

    def _study_sec(self):
        return self._clamp_int(self.config.get("study_min", 20), 20, 1, 120) * 60

    def _short_break_sec(self):
        return self._clamp_int(self.config.get("break_min", 5), 5, 1, 60) * 60

    def _long_break_sec(self):
        return self._clamp_int(self.config.get("long_break_min", 15), 15, 1, 180) * 60

    def _long_break_every(self):
        return self._clamp_int(self.config.get("long_break_every", 4), 4, 1, 20)

    def _set_phase(self, phase, duration_sec, break_kind="SHORT"):
        self.phase = phase
        self.break_kind = break_kind
        self.phase_started_elapsed = self._effective_elapsed()
        self.phase_duration_sec = max(1, int(duration_sec))

    def _next_break_kind(self):
        next_index = self.completed_study_blocks + 1
        return "LONG" if next_index % self._long_break_every() == 0 else "SHORT"

    def _break_duration_sec_for_kind(self, kind):
        return self._long_break_sec() if kind == "LONG" else self._short_break_sec()

    def _current_break_elapsed_seconds(self):
        if self.phase != "BREAK":
            return 0.0
        return max(0.0, self._effective_elapsed() - self.phase_started_elapsed)

    def _record_current_break_elapsed(self):
        if self.phase == "BREAK":
            self.total_break_seconds += self._current_break_elapsed_seconds()

    def _transition_to_break(self, kind=None):
        selected_kind = kind or self._next_break_kind()
        self.completed_study_blocks += 1
        if selected_kind == "LONG":
            self.completed_long_breaks += 1
        self.pending_break_offer = False
        self.pending_return_offer = False
        self.pending_break_kind = "SHORT"
        self.pending_break_duration_sec = 0
        self._set_phase(
            "BREAK",
            self._break_duration_sec_for_kind(selected_kind),
            break_kind=selected_kind,
        )

    def _transition_to_study(self):
        if self.phase == "BREAK":
            self._record_current_break_elapsed()
            self.completed_breaks += 1
        self.pending_break_offer = False
        self.pending_return_offer = False
        self.pending_break_kind = "SHORT"
        self.pending_break_duration_sec = 0
        self._set_phase("STUDY", self._study_sec(), break_kind="SHORT")

    def _extend_break(self, seconds=60):
        self._record_current_break_elapsed()
        self.pending_return_offer = False
        self.phase_started_elapsed = self._effective_elapsed()
        self.phase_duration_sec = max(30, int(seconds))

    def skip_break(self):
        if self.pending_break_offer:
            self.completed_study_blocks += 1
            self.pending_break_offer = False
            self.pending_break_kind = "SHORT"
            self.pending_break_duration_sec = 0
            self._set_phase("STUDY", self._study_sec(), break_kind="SHORT")
            return
        if self.phase == "BREAK":
            self._transition_to_study()

    def start_break(self):
        if self.pending_break_offer:
            self._transition_to_break(self.pending_break_kind)
            return
        if self.phase != "BREAK":
            self._transition_to_break(self._next_break_kind())

    def respond_to_break_offer(self, take_break):
        if not self.pending_break_offer:
            return False
        if take_break:
            self._transition_to_break(self.pending_break_kind)
        else:
            self.completed_study_blocks += 1
            self.pending_break_offer = False
            self.pending_break_kind = "SHORT"
            self.pending_break_duration_sec = 0
            self._set_phase("STUDY", self._study_sec(), break_kind="SHORT")
        return True

    def respond_to_study_offer(self, return_to_study):
        if not self.pending_return_offer:
            return False
        if return_to_study:
            self._transition_to_study()
        else:
            self._extend_break(60)
        return True

    def card_answered(self, latency, ease):
        if not self.is_active or self.is_paused:
            return

        self.cards_studied += 1
        is_again = ease == 1
        self.latencies.append((latency, is_again))
        if len(self.latencies) > 20:
            self.latencies.pop(0)
        if is_again:
            self.again_count += 1

    def _effective_elapsed(self):
        if not self.is_active:
            return 0.0

        now = time.time()
        if self.is_paused:
            now = self.pause_started_at

        elapsed = now - self.start_time - self.total_paused_seconds
        return max(0.0, elapsed)

    def get_phase_info(self):
        if not self.is_active:
            return "STUDY", 0, 0, False, False, "SHORT", None

        elapsed = self._effective_elapsed()
        transition_triggered = False
        phase_elapsed = elapsed - self.phase_started_elapsed
        prompt_type = None

        if not self.is_paused:
            if self.phase == "STUDY" and phase_elapsed >= self.phase_duration_sec:
                if not self.pending_break_offer:
                    self.pending_break_offer = True
                    self.pending_break_kind = self._next_break_kind()
                    self.pending_break_duration_sec = self._break_duration_sec_for_kind(
                        self.pending_break_kind
                    )
                    transition_triggered = True
                prompt_type = "ASK_BREAK"
            elif self.phase == "BREAK" and phase_elapsed >= self.phase_duration_sec:
                if not self.pending_return_offer:
                    self.pending_return_offer = True
                    transition_triggered = True
                prompt_type = "ASK_STUDY"

        if self.pending_break_offer:
            prompt_type = "ASK_BREAK"
        elif self.pending_return_offer:
            prompt_type = "ASK_STUDY"

        if self.pending_break_offer or self.pending_return_offer:
            remaining = 0
        else:
            remaining = int(max(0, self.phase_duration_sec - phase_elapsed))
        return (
            self.phase,
            remaining,
            int(elapsed),
            transition_triggered,
            self.is_paused,
            self.break_kind,
            prompt_type,
        )

    def get_pending_break_details(self):
        if not self.pending_break_offer:
            return None
        summary = self.get_session_summary() or {}
        return {
            "kind": self.pending_break_kind,
            "duration_sec": int(self.pending_break_duration_sec),
            "cards": int(summary.get("cards", self.cards_studied)),
            "avg_score": float(summary.get("avg_score", round(self.smoothed_score, 1))),
            "stability": float(summary.get("stability", 50.0)),
            "best_focus_minutes": float(summary.get("best_focus_minutes", 0.0)),
            "avg_focus_streak_minutes": float(summary.get("avg_focus_streak_minutes", 0.0)),
        }

    def calculate_cognitive_score(self):
        if not self.is_active:
            return 50

        min_cards = int(self.config.get("calibration_cards", 5))
        min_cards = max(3, min(20, min_cards))
        if len(self.latencies) < 2:
            return int(round(self.smoothed_score))

        recent = self.latencies[-30:]
        recent_latencies = [x[0] for x in recent]
        recent_again_count = sum(1 for x in recent if x[1])

        baseline = 50.0
        sensitivity = float(self.config.get("sensitivity", 0.5))
        sensitivity = max(0.0, min(1.0, sensitivity))

        current_acc = 1.0 - (recent_again_count / (len(recent) + 0.0001))
        acc_delta = (current_acc - 0.85) * 58.0

        avg = sum(recent_latencies) / len(recent_latencies)
        var = sum((x - avg) ** 2 for x in recent_latencies) / (len(recent_latencies) + 0.0001)
        jitter = math.sqrt(var) / (avg + 0.1)
        jitter_delta = (0.35 - jitter) * 34.0

        raw_score = baseline + (acc_delta + jitter_delta) * sensitivity
        raw_score = max(0.0, min(100.0, raw_score))

        confidence = min(1.0, len(self.latencies) / float(max(min_cards * 2, 10)))
        target_score = baseline * (1.0 - confidence) + raw_score * confidence

        alpha = 0.12 + (0.28 * sensitivity)
        if len(self.latencies) < min_cards:
            alpha *= 0.55

        self.smoothed_score += alpha * (target_score - self.smoothed_score)
        self.smoothed_score = max(0.0, min(100.0, self.smoothed_score))
        return int(round(self.smoothed_score))

    def record_score_sample(self, score):
        if not self.is_active or self.is_paused:
            return

        elapsed = self._effective_elapsed()
        if self.last_score_sample_elapsed is None:
            delta_sec = 1.0
        else:
            delta_sec = max(0.0, elapsed - self.last_score_sample_elapsed)
            if delta_sec == 0.0:
                delta_sec = 1.0

        self.last_score_sample_elapsed = elapsed
        self.score_samples.append(int(score))
        if len(self.score_samples) > 4000:
            self.score_samples.pop(0)

        self.score_sum += float(score)
        self.score_count += 1

        # Focus streak tracks sustained focused study periods, not break periods.
        in_focus_window = (
            self.phase == "STUDY"
            and not self.pending_break_offer
            and int(score) >= self.FOCUS_THRESHOLD
        )
        if in_focus_window:
            self.current_focus_streak_sec += delta_sec
            if self.current_focus_streak_sec > self.best_focus_streak_sec:
                self.best_focus_streak_sec = self.current_focus_streak_sec
        else:
            if self.current_focus_streak_sec > 0.0:
                self.focus_streak_total_sec += self.current_focus_streak_sec
                self.focus_streak_count += 1
            self.current_focus_streak_sec = 0.0

    def get_session_summary(self):
        if self.cards_studied <= 0 and self.score_count <= 0:
            return None

        avg_score = 50.0
        if self.score_count > 0:
            avg_score = self.score_sum / float(self.score_count)

        stability = 50.0
        if len(self.score_samples) >= 2:
            avg = sum(self.score_samples) / float(len(self.score_samples))
            var = sum((x - avg) ** 2 for x in self.score_samples) / float(len(self.score_samples))
            stddev = math.sqrt(var)
            stability = max(0.0, min(100.0, 100.0 - (stddev * 2.5)))

        focus_total_sec = float(self.focus_streak_total_sec)
        focus_count = int(self.focus_streak_count)
        if self.current_focus_streak_sec > 0.0:
            focus_total_sec += self.current_focus_streak_sec
            focus_count += 1

        avg_focus_streak_minutes = 0.0
        if focus_count > 0:
            avg_focus_streak_minutes = (focus_total_sec / float(focus_count)) / 60.0

        return {
            "cards": int(self.cards_studied),
            "avg_score": round(avg_score, 1),
            "stability": round(stability, 1),
            "paused_minutes": round(self.total_paused_seconds / 60.0, 1),
            "break_minutes": round(
                (self.total_break_seconds + self._current_break_elapsed_seconds()) / 60.0,
                1,
            ),
            "best_focus_minutes": round(self.best_focus_streak_sec / 60.0, 1),
            "avg_focus_streak_minutes": round(avg_focus_streak_minutes, 1),
            "long_breaks": int(self.completed_long_breaks),
        }
