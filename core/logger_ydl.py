class MyLogger:
    def trace(self, msg: str) -> None:
        print(f'tr**{msg}')

    def debug(self, msg: str) -> None:
        print(f'++{msg}')

    def info(self, msg: str) -> None:
        print(f'inf**{msg}')

    def warning(self, msg: str) -> None:
        print(msg)

    def error(self, msg: str) -> None:
        print(msg)
