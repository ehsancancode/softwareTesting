import unittest
from User_Registration import (
    UserRegistration,
    is_valid_email,
    is_strong_password,
    hash_password,
    check_password,
)

class TestUserRegistration(unittest.TestCase):
    """UT for User Registration Module"""

    def setUp(self):
        self.reg = UserRegistration()

    # ---------------- Email Validation ----------------
    def test_valid_email(self):
        self.assertTrue(is_valid_email("student@example.com"))
        self.assertTrue(is_valid_email("user.name123@domain.co.uk"))

    def test_invalid_email(self):
        self.assertFalse(is_valid_email("invalidemail"))
        self.assertFalse(is_valid_email("user@domain"))
        self.assertFalse(is_valid_email("@domain.com"))

    # ---------------- Password Strength ----------------
    def test_strong_password_valid(self):
        self.assertTrue(is_strong_password("StrongPass123!"))

    def test_strong_password_invalid(self):
        self.assertFalse(is_strong_password("weakpass"))
        self.assertFalse(is_strong_password("12345678"))
        self.assertFalse(is_strong_password("NoSpecialChar1"))

    # ---------------- Password Hashing ----------------
    def test_password_hash_and_check(self):
        password = "SecurePass123!"
        hashed = hash_password(password)
        self.assertNotEqual(password, hashed)
        self.assertTrue(check_password(password, hashed))
        self.assertFalse(check_password("WrongPass", hashed))

    # ---------------- User Registration Logic ----------------
    def test_register_valid_user(self):
        user = {"email": "test@example.com", "password": "GoodPass123!"}
        result = self.reg.register_user(user)
        self.assertTrue(result)

    def test_register_duplicate_email(self):
        user1 = {"email": "test@example.com", "password": "GoodPass123!"}
        user2 = {"email": "Test@Example.com", "password": "AnotherPass123!"}
        self.reg.register_user(user1)
        result = self.reg.register_user(user2)
        self.assertFalse(result["success"])

    def test_register_invalid_email(self):
        user = {"email": "bademail", "password": "ValidPass123!"}
        result = self.reg.register_user(user)
        self.assertFalse(result["success"])

    def test_register_weak_password(self):
        user = {"email": "weakpass@example.com", "password": "1234567"}
        result = self.reg.register_user(user)
        self.assertFalse(result["success"])
        
if __name__ == "__main__":
    unittest.main()
