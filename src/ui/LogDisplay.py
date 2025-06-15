import logging


class LogDisplay(logging.Handler):
    def __init__(self, logView):
        super().__init__()
        self.view = logView
        self.logs = []  # Store logs in memory to update the widget

    def emit(self, record):
        # Format the log message
        log_entry = self.format(record)
        self.logs.append(log_entry)  # Accumulate logs
        # Update the widget with all logs as HTML (e.g., with <br> for line breaks)
        self.widget.value = "<br>".join(self.logs)
