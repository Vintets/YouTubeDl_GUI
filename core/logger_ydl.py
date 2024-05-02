class MyLogger:
    def trace(self, msg):
        print(f'tr**{msg}')

    def debug(self, msg):
        print(f'++{msg}')

    def info(self, msg):
        print(f'inf**{msg}')

    def warning(self, msg):
        print(msg)

    def error(self, msg):
        print(msg)
