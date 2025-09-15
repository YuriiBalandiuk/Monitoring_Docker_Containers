import logger_setup.logger as lc
from telegram_bot_alerts import setup_alerts


def main() -> int:
    """
    Main entry point of the application.

    This function initializes the logger, starts the Telegram bot for alerts,
    and returns 0 upon successful execution.

    Steps:
    1. Logs that the application has started.
    2. Starts the Telegram bot using `setup_alerts.start_telegram_bot()`.
    3. Returns 0 when execution completes successfully.
    """
    lc.logger.info("The app has started!")
    setup_alerts.start_telegram_bot()
    return 0


if __name__ == "__main__":
    END = main()
    if END == 0:
        lc.logger.info("The app is complete!")
