import logging


class AppLog:
    """ログをコンソールへ出力する"""

    def __init__(self):
        logger = logging.getLogger("ash_aed_log")
        logger.setLevel(logging.DEBUG)
        if not logger.handlers == []:
            for exist_handler in logger.handlers:
                logger.removeHandler(exist_handler)
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(formatter)
        self.__logger = logger
        self.__logger.addHandler(console_handler)

    def debug(self, message) -> None:
        """logging.debugのラッパー

        Args:
            message (str): デバッグログメッセージ

        """
        return self.__logger.debug(message)

    def info(self, message) -> None:
        """logging.infoのラッパー

        Args:
            message (str): 通常のログメッセージ

        """
        return self.__logger.info(message)

    def warning(self, message) -> None:
        """logging.warningのラッパー

        Args:
            message (str): 警告ログメッセージ

        """
        return self.__logger.warning(message)

    def error(self, message) -> None:
        """logging.errorのラッパー

        Args:
            message (str): エラーログメッセージ

        """
        return self.__logger.error(message)

    def critical(self, message) -> None:
        """logging.criticalのラッパー

        Args:
            message (str): 重大なエラーログメッセージ

        """
        return self.__logger.critical(message)
