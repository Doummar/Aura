
from aqt import mw
class ProgressEngine:
    @staticmethod
    def get_remaining():
        if not mw.col: return 0
        try: return sum(mw.col.sched.counts())
        except: return 0
