import logging

class DuplicateFilter(logging.Filter):
    def __init__(self, name=''):
        super().__init__(name)
        self.last_log = None

    def filter(self, record):
        current_log = (record.module, record.levelno, record.msg)
        if current_log != self.last_log:
            self.last_log = current_log
            return True
        return False