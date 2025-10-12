import re
import hashlib

class UserRegistration:
    def __init__(self):
        self.users = {}

    def register_user(self, user):
        """
        Registers a new user. Expects a dict with 'email' and 'password'.
        Returns True if successful, False otherwise.
        """
        email = user.get("email")
        password = user.get("password")

        if not is_valid_email(email):
            return False
        if not is_strong_password(password):
            return False
        if any(u.lower() == email.lower() for u in self.users):
            return False  # duplicate (case-insensitive)

        # Hash and store password
        hashed = hash_password(password)
        self.users[email.lower()] = hashed
        return True
    
# ---------------- Utility Functions ----------------

def is_valid_email(email):
    """Simple regex for validating an email."""
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None

def is_strong_password(password):
    """Check length >= 8, contains upper, lower, digit, and special char."""
    return (
            len(password) >= 8
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
