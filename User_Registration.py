import re
import hashlib

class UserRegistration:
    def __init__(self):
        self.users = {}

    def register(self, email, password, confirm_password):
        """
        Registers a new user directly from email/password form.
        Returns a dict with {success: bool, message: str}.
        """
        # Basic validation
        if not email or not password:
            return {"success": False, "error": "Email and password are required"}

        email = email.strip().lower()

        if not is_valid_email(email):
            return {"success": False, "error": "Invalid email format"}

        if password != confirm_password:
            return {"success": False, "error": "Passwords do not match"}

        if not is_strong_password(password):
            return {"success": False, "error": "Password too weak (must include upper, lower, digit, symbol)"}

        if email in self.users:
            return {"success": False, "error": "Email already registered"}

        # Hash and store password securely
        hashed = hash_password(password)
        self.users[email] = {"password": hashed, "confirmed": False}

        return {"success": True, "message": "Registration successful"}

    # (Optional) for programmatic tests
    def register_user(self, user):
        """Compatibility with your test_user_registration file."""
        return self.register(user["email"], user["password"], user["password"])


# ---------------- Utility Functions ----------------

def is_valid_email(email):
    """Simple regex for validating an email."""
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email or "") is not None

def is_strong_password(password):
    """Check length >= 8, contains upper, lower, digit, and special char."""
    return (
            len(password or "") >= 8
            and any(c.islower() for c in password)
            and any(c.isupper() for c in password)
            and any(c.isdigit() for c in password)
            and any(not c.isalnum() for c in password)
    )

def hash_password(password):
    """Hash a password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(password, hashed):
    """Compare a password with its hashed version."""
    return hash_password(password) == hashed
