from aqt import gui_hooks, mw
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QAction

from .session_manager import SessionManager
from ..hooks.reviewer_hooks import ReviewerHooks
from ..persistence.config import AuraConfig
from ..ui.overlay_window import HUDOverlay


def init():
    gui_hooks.profile_did_open.append(setup_aura)


def setup_aura():
    if hasattr(mw, "aura_v5_active"):
        old = mw.aura_v5_active
        try:
            old["hooks"].teardown()
        except Exception:
            pass
        try:
            old["overlay"].hide()
            old["overlay"].timer.stop()
        except Exception:
            pass

    config = AuraConfig()
    manager = SessionManager(config)
    overlay = HUDOverlay(manager, config)
    hooks = ReviewerHooks(manager, overlay)
    hooks.setup()

    mw.aura_v5_active = {
        "overlay": overlay,
        "manager": manager,
        "config": config,
        "hooks": hooks,
    }

    if not hasattr(mw, "aura_v5_action"):
        action = QAction("Aura Settings", mw)
        action.triggered.connect(open_settings)
        mw.form.menuTools.addAction(action)
        mw.aura_v5_action = action

    # Show the help guide automatically on first install
    if config.get("first_run", True):
        config.set("first_run", False)
        QTimer.singleShot(600, _show_welcome)


def _show_welcome():
    try:
        from ..ui.help_window import HelpWindow
        HelpWindow(mw).exec()
    except Exception:
        pass


def open_settings():
    if not hasattr(mw, "aura_v5_active"):
        return

    from ..ui.settings_window import SettingsWindow

    config = mw.aura_v5_active["config"]
    overlay = mw.aura_v5_active["overlay"]

    diag = SettingsWindow(config, mw)
    if diag.exec():
        overlay.apply_styles()
        overlay.refresh()


def open_help():
    from ..ui.help_window import HelpWindow

    diag = HelpWindow(mw)
    diag.exec()
