# tests/test_main_app_logic.py
import unittest
from unittest import mock
import main

def fake_tk_init(self):
    """Fake __init__ to replace tkinter.Tk.__init__ for headless testing."""
    self.tk = mock.MagicMock()
    self._w = "mock_root"  # Tk expects a window name string
    return None

class TestMainApplicationLogic(unittest.TestCase):
    """Covers non-UI logic inside main.Application and frame methods."""

    @mock.patch("tkinter.Tk.__init__", new=fake_tk_init)
    def test_application_initialization_loads_users(self):
        app = main.Application()
        # Registration object should exist
        self.assertIsInstance(app.registration.users, dict)
        self.assertIsNone(app.logged_in_email)
        # App should auto-load startup frame
        self.assertIsInstance(app.current_frame, main.StartupFrame)

    @mock.patch("tkinter.Tk.__init__", new=fake_tk_init)
    def test_show_frame_methods_do_not_crash(self):
        app = main.Application()
        with mock.patch.object(main.tk.Frame, "pack"), mock.patch.object(main.tk.Frame, "destroy"):
            app.show_startup_frame()
            app.show_register_frame()
            app.show_login_frame()
        self.assertIsNotNone(app.current_frame)

    @mock.patch("tkinter.messagebox.showerror")
    @mock.patch("tkinter.messagebox.showinfo")
    @mock.patch("tkinter.Tk.__init__", new=fake_tk_init)
    def test_register_user_branch_success_and_failure(self, mock_info, mock_error):
        app = main.Application()
        frame = main.RegisterFrame(app)

        # Success case
        frame.email_entry.get = lambda: "test@example.com"
        frame.pass_entry.get = lambda: "StrongPass1!"
        frame.conf_pass_entry.get = lambda: "StrongPass1!"
        app.registration.register = lambda e, p, c: {"success": True}
        frame.register_user()
        mock_info.assert_called_once()

        # Failure case
        app.registration.register = lambda e, p, c: {"success": False, "error": "Invalid input"}
        frame.register_user()
        mock_error.assert_called_once()

    @mock.patch("tkinter.messagebox.showerror")
    @mock.patch("tkinter.Tk.__init__", new=fake_tk_init)
    def test_login_validation_paths(self, mock_error):
        app = main.Application()
        frame = main.LoginFrame(app)

        # Invalid login path
        frame.email_entry.get = lambda: "unknown@example.com"
        frame.pass_entry.get = lambda: "wrong"
        app.registration.users = {"known@example.com": {"password": "goodpass"}}
        frame.login()
        mock_error.assert_called_once()

        # Valid login path
        called = {}
        app.login_user = lambda email: called.setdefault("ok", email)
        frame.email_entry.get = lambda: "known@example.com"
        frame.pass_entry.get = lambda: "goodpass"
        frame.login()
        self.assertEqual(called["ok"], "known@example.com")
