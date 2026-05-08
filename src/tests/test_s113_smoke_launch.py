"""S1-13: Smoke tests for application startup (no GUI window opened)."""
import logging
import logging.config
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Make sure src/ is on path so imports resolve the same way as in app_main.py
SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)


class TestLoggingSetup(unittest.TestCase):
    """logging.conf is present and valid."""

    def test_logging_conf_is_parseable(self):
        """logging.conf can be loaded by fileConfig without raising."""
        conf_path = os.path.join(SRC_DIR, "logging.conf")
        self.assertTrue(os.path.exists(conf_path), "logging.conf missing from src/")
        try:
            logging.config.fileConfig(conf_path)
        except Exception as e:
            self.fail(f"logging.config.fileConfig raised {type(e).__name__}: {e}")

    def test_logs_directory_created(self):
        """start_application() creates logs/ directory when absent."""
        import app_main

        target_logs = os.path.join(os.path.dirname(SRC_DIR), "logs")
        # Directory may or may not exist; either way, function must not raise.
        with patch("app_main.MainAppController") as mock_ctrl:
            mock_ctrl.return_value.Run.return_value = None
            original_cwd = os.getcwd()
            try:
                os.chdir(os.path.dirname(SRC_DIR))
                app_main.startApplication()
                self.assertTrue(os.path.isdir("logs"), "logs/ directory was not created")
            finally:
                os.chdir(original_cwd)


class TestStartApplicationWithConf(unittest.TestCase):
    """startApplication() succeeds when logging.conf is present."""

    def test_runs_without_exception(self):
        import app_main

        with patch("app_main.MainAppController") as mock_ctrl:
            mock_ctrl.return_value.Run.return_value = None
            original_cwd = os.getcwd()
            try:
                os.chdir(os.path.dirname(SRC_DIR))
                app_main.startApplication()
            except Exception as e:
                self.fail(f"startApplication() raised unexpectedly: {e}")
            finally:
                os.chdir(original_cwd)

        mock_ctrl.assert_called_once()
        mock_ctrl.return_value.Run.assert_called_once()


class TestStartApplicationFallbackLogging(unittest.TestCase):
    """startApplication() falls back gracefully when logging.conf is absent."""

    def test_fallback_when_conf_missing(self):
        import app_main

        with patch("app_main.MainAppController") as mock_ctrl, \
             patch("logging.config.fileConfig", side_effect=FileNotFoundError("mocked missing")):
            mock_ctrl.return_value.Run.return_value = None
            original_cwd = os.getcwd()
            try:
                os.chdir(os.path.dirname(SRC_DIR))
                app_main.startApplication()
            except Exception as e:
                self.fail(f"startApplication() raised when logging.conf missing: {e}")
            finally:
                os.chdir(original_cwd)

        # App still started even without the config file
        mock_ctrl.assert_called_once()

    def test_fallback_when_conf_corrupt(self):
        """startApplication() falls back when logging.conf has a parse error."""
        import app_main
        import configparser

        with patch("app_main.MainAppController") as mock_ctrl, \
             patch("logging.config.fileConfig",
                   side_effect=configparser.Error("mocked parse error")):
            mock_ctrl.return_value.Run.return_value = None
            original_cwd = os.getcwd()
            try:
                os.chdir(os.path.dirname(SRC_DIR))
                app_main.startApplication()
            except Exception as e:
                self.fail(f"startApplication() raised on corrupt logging.conf: {e}")
            finally:
                os.chdir(original_cwd)

        mock_ctrl.assert_called_once()


if __name__ == "__main__":
    unittest.main()
