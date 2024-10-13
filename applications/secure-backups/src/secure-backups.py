from sighandler.sighandler import SignalHandler


def process_backups():
    signal_handler = SignalHandler()

    while signal_handler.can_run():
        pass


if __name__ == "__main__":
    process_backups()
