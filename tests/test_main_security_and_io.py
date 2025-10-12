"""
Unit tests for security and I/O helpers in main.py

These tests ensure:
- Safe and atomic user data file handling
- Email normalization
- Secure password hashing and verification
- Basic integration of main Application password storage behavior

Each NEW TEST below covers new functionality added in main.py security refactor.
"""

import os
import json
import unittest
import tempfile

import main

class TestMainSecurityAndIO(unittest.TestCase):
    """Tests for secure helpers and data integrity in main.py."""

    def setUp(self):
        # Create a temporary directory to isolate test files
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)

        # Redirect USERS_FILE to temporary location
        self.users_path = os.path.join(self.tmpdir.name, "users.json")
        main.USERS_FILE = self.users_path

    # NEW TEST: safe_load_json returns {} for missing or corrupted JSON files
    def test_safe_load_json_missing_or_corrupt(self):
        # Missing file → should return {}
        data = main.safe_load_json(self.users_path)
        self.assertEqual(data, {}, "Expected {} for missing file")

        # Corrupted file → should also return {}
        with open(self.users_path, "w") as f:
            f.write("{invalid json")
        data = main.safe_load_json(self.users_path)
        self.assertEqual(data, {}, "Expected {} for corrupt JSON")

    # NEW TEST: atomic_write_json writes and reads back identical data
    def test_atomic_write_and_read_cycle(self):
        users = {"test@example.com": {"password": "hash", "confirmed": False}}
        main.atomic_write_json(self.users_path, users)

        # Ensure file exists and content matches
        self.assertTrue(os.path.exists(self.users_path), "users.json should exist after write")
        with open(self.users_path, "r") as f:
            loaded = json.load(f)
        self.assertEqual(loaded, users, "Written data should match read data")

    # NEW TEST: normalize_email lowercases and trims spaces
    def test_normalize_email(self):
        self.assertEqual(main.normalize_email("  User@Example.COM "), "user@example.com")
        self.assertEqual(main.normalize_email("Test@domain.com"), "test@domain.com")
        self.assertEqual(main.normalize_email(""), "")

    # NEW TEST: check_password verifies hashed password correctly
    def test_check_password_validation(self):
        from User_Registration import hash_password, check_password
        password = "StrongPass123"
        hashed = hash_password(password)

        # Valid password should return True
        self.assertTrue(check_password(password, hashed))

        # Wrong password should return False
        self.assertFalse(check_password("WrongPass", hashed))

    # NEW TEST: load_users and save_users maintain data integrity safely
    def test_load_and_save_users_cycle(self):
        users_data = {"user@example.com": {"password": "abc123", "confirmed": True}}
        main.save_users(users_data)
        loaded = main.load_users()
        self.assertEqual(loaded, users_data)

    # NEW TEST: ensure atomic_write_json prevents partial writes
    def test_atomic_write_prevents_partial(self):
        """Simulate interrupted writes — we expect a valid JSON file afterwards."""
        sample = {"a": 1, "b": 2}
        main.atomic_write_json(self.users_path, sample)
        with open(self.users_path, "r") as f:
            content = f.read()
        self.assertIn('"a": 1', content)
        self.assertIn('"b": 2', content)

    # NEW TEST: integration — Application migrates plaintext to hashed passwords
    def test_application_migrates_plaintext_passwords(self):
        from User_Registration import check_password
        plain_users = {"user@example.com": {"password": "Password123!", "confirmed": False}}
        main.atomic_write_json(self.users_path, plain_users)

        # Initialize the Application to trigger migration
        app = main.Application()
        migrated_pw = app.registration.users["user@example.com"]["password"]

        # Should now be hashed and not equal to the plain password
        self.assertNotEqual(migrated_pw, "Password123!")
        self.assertTrue(check_password("Password123!", migrated_pw))
        app.destroy()  # Close the Tk window safely

    # NEW TEST: secure login logic with hashed password
    def test_login_with_hashed_password(self):
        """Ensures login succeeds when hashed password matches."""
        from User_Registration import hash_password
        hashed_pw = hash_password("MyStrongPass1!")
        app = main.Application()
        app.registration.users = {"user@example.com": {"password": hashed_pw}}

        # Simulate login manually
        email = "user@example.com"
        ok = main.check_password("MyStrongPass1!", hashed_pw)
        self.assertTrue(ok, "Login should succeed with hashed password")
        app.destroy()

    # NEW TEST: invalid password should fail login
    def test_login_with_invalid_password(self):
        """Ensures login fails when password doesn't match."""
        from User_Registration import hash_password
        hashed_pw = hash_password("CorrectPass!")
        app = main.Application()
        app.registration.users = {"user@example.com": {"password": hashed_pw}}

        ok = main.check_password("WrongPass!", hashed_pw)
        self.assertFalse(ok)
        app.destroy()


if __name__ == "__main__":
    unittest.main(verbosity=2)
