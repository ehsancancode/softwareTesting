import tkinter as tk
from tkinter import messagebox, ttk
import json
import os

# 🔐 Import hashing/checking utilities to use secure password verification
from User_Registration import UserRegistration, check_password
from Order_Placement import Cart, OrderPlacement, UserProfile, RestaurantMenu, PaymentMethod
from Payment_Processing import PaymentProcessing
from Restaurant_Browsing import RestaurantDatabase, RestaurantBrowsing


# ---------------------- SECURITY & IO HELPERS ----------------------

USERS_FILE = "users.json"

def normalize_email(email: str) -> str:
    """Normalize email to lowercase and remove extra spaces."""
    return (email or "").strip().lower()

def safe_load_json(path: str) -> dict:
    """Load a JSON file safely, returning {} if missing or corrupted."""
    try:
        if not os.path.exists(path):
            return {}
        with open(path, "r") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}

def atomic_write_json(path: str, data: dict):
    """Write JSON atomically to avoid corruption and set secure permissions."""
    tmp_path = path + ".tmp"
    with open(tmp_path, "w") as f:
        json.dump(data, f, indent=4)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_path, path)
    try:
        os.chmod(path, 0o600)  # restrict file permissions where possible
    except Exception:
        pass

def load_users():
    """Load users safely from JSON file."""
    return safe_load_json(USERS_FILE)

def save_users(users):
    """Save users safely to JSON file."""
    atomic_write_json(USERS_FILE, users)


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mobile Food Delivery App")
        self.geometry("600x400")

        # ✅ Use safe file loading for user data
        self.user_data = load_users()

        # Initialize core classes
        self.registration = UserRegistration()
        self.registration.users = self.user_data  # Load existing users into registration system

        self.database = RestaurantDatabase()
        self.browsing = RestaurantBrowsing(self.database)

        # Initially no user logged in
        self.logged_in_email = None

        # One-time password upgrade (migrate plaintext to hashed)
        from User_Registration import hash_password, is_strong_password
        updated = False
        """fix for one UT failure"""
        updated = False
        for email, data in self.registration.users.items():
            pw = data.get("password", "")
            # Detect plaintext: bcrypt hashes always start with "$2" or "$argon2"
            if pw and not str(pw).startswith(("$2", "$argon2")):
                # Only hash if password looks reasonably strong
                if is_strong_password(pw):
                    self.registration.users[email]["password"] = hash_password(pw)
                    updated = True
        if updated:
            save_users(self.registration.users)

        # Create initial frame
        self.current_frame = None
        self.show_startup_frame()

    def show_startup_frame(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = StartupFrame(self)
        self.current_frame.pack(fill="both", expand=True)

    def show_register_frame(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = RegisterFrame(self)
        self.current_frame.pack(fill="both", expand=True)

    def show_login_frame(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = LoginFrame(self)
        self.current_frame.pack(fill="both", expand=True)

    def login_user(self, email):
        self.logged_in_email = email
        # After login, show main app frame
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = MainAppFrame(self, email)
        self.current_frame.pack(fill="both", expand=True)


class StartupFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        tk.Label(self, text="Welcome to the Mobile Food Delivery App", font=("Arial", 16)).pack(pady=30)

        tk.Button(self, text="Register", command=self.go_to_register, width=20).pack(pady=10)
        tk.Button(self, text="Login", command=self.go_to_login, width=20).pack(pady=10)

    def go_to_register(self):
        self.master.show_register_frame()

    def go_to_login(self):
        self.master.show_login_frame()


class RegisterFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        tk.Label(self, text="Register New User", font=("Arial", 14)).pack(pady=20)

        self.email_entry = self.create_entry("Email:")
        self.pass_entry = self.create_entry("Password:", show="*")
        self.conf_pass_entry = self.create_entry("Confirm Password:", show="*")

        tk.Button(self, text="Register", command=self.register_user).pack(pady=10)
        tk.Button(self, text="Back", command=self.go_back).pack()

    def create_entry(self, label_text, show=None):
        frame = tk.Frame(self)
        frame.pack(pady=5)
        tk.Label(frame, text=label_text, width=15, anchor="e").pack(side="left")
        entry = tk.Entry(frame, show=show)
        entry.pack(side="left")
        return entry

    def register_user(self):
        # Normalize email before registering
        email = normalize_email(self.email_entry.get())
        password = self.pass_entry.get()
        confirm_password = self.conf_pass_entry.get()

        result = self.master.registration.register(email, password, confirm_password)
        if result["success"]:
            save_users(self.master.registration.users)
            messagebox.showinfo("Success", "Registration successful! Please log in.")
            self.master.show_login_frame()
        else:
            messagebox.showerror("Error", result["error"])

    def go_back(self):
        self.master.show_startup_frame()


class LoginFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        tk.Label(self, text="User Login", font=("Arial", 14)).pack(pady=20)

        self.email_entry = self.create_entry("Email:")
        self.pass_entry = self.create_entry("Password:", show="*")

        tk.Button(self, text="Login", command=self.login).pack(pady=10)
        tk.Button(self, text="Back", command=self.go_back).pack()

    def create_entry(self, label_text, show=None):
        frame = tk.Frame(self)
        frame.pack(pady=5)
        tk.Label(frame, text=label_text, width=15, anchor="e").pack(side="left")
        entry = tk.Entry(frame, show=show)
        entry.pack(side="left")
        return entry

    def login(self):
        # Secure login using hashed passwords & normalized emails
        email = normalize_email(self.email_entry.get())
        password = self.pass_entry.get()
        users = self.master.registration.users

        if email in users:
            stored = users[email]
            stored_pw = stored.get("password", "")
            ok = False
            try:
                ok = check_password(password, stored_pw)
            except Exception:
                ok = False

            # Allow temporary fallback for legacy plaintext users
            if not ok and stored_pw == password:
                ok = True

            if ok:
                self.master.login_user(email)
                return

        messagebox.showerror("Error", "Invalid email or password")

    def go_back(self):
        self.master.show_startup_frame()


class MainAppFrame(tk.Frame):
    def __init__(self, master, user_email):
        super().__init__(master)
        tk.Label(self, text=f"Welcome, {user_email}", font=("Arial", 14)).pack(pady=10)

        self.user_email = user_email
        self.database = master.database
        self.browsing = master.browsing

        # Create user's profile and cart
        self.user_profile = UserProfile(delivery_address="123 Main St")
        self.cart = Cart()
        self.restaurant_menu = RestaurantMenu(available_items=["Burger", "Pizza", "Salad"])
        self.order_placement = OrderPlacement(self.cart, self.user_profile, self.restaurant_menu)

        # Search Frame
        search_frame = tk.Frame(self)
        search_frame.pack(pady=10)
        tk.Label(search_frame, text="Cuisine:").pack(side="left")
        self.cuisine_var = tk.Entry(search_frame)
        self.cuisine_var.pack(side="left", padx=5)
        tk.Button(search_frame, text="Search", command=self.search_restaurants).pack(side="left")

        # Results Treeview
        self.results_tree = ttk.Treeview(self, columns=("cuisine", "location", "rating"), show="headings")
        self.results_tree.heading("cuisine", text="Cuisine")
        self.results_tree.heading("location", text="Location")
        self.results_tree.heading("rating", text="Rating")
        self.results_tree.pack(pady=10, fill="x")

        # Buttons for actions
        action_frame = tk.Frame(self)
        action_frame.pack(pady=5)
        tk.Button(action_frame, text="View All Restaurants", command=self.view_all_restaurants).pack(side="left", padx=5)
        tk.Button(action_frame, text="Add Item to Cart", command=self.add_item_to_cart).pack(side="left", padx=5)
        tk.Button(action_frame, text="View Cart", command=self.view_cart).pack(side="left", padx=5)
        tk.Button(action_frame, text="Checkout", command=self.checkout).pack(side="left", padx=5)

    def search_restaurants(self):
        self.results_tree.delete(*self.results_tree.get_children())
        cuisine = self.cuisine_var.get().strip()
        results = self.browsing.search_by_filters(cuisine_type=cuisine if cuisine else None)
        for r in results:
            self.results_tree.insert("", "end", values=(r["cuisine"], r["location"], r["rating"]))

    def view_all_restaurants(self):
        self.results_tree.delete(*self.results_tree.get_children())
        results = self.database.get_restaurants()
        for r in results:
            self.results_tree.insert("", "end", values=(r["cuisine"], r["location"], r["rating"]))

    def add_item_to_cart(self):
        menu_popup = AddItemPopup(self, self.restaurant_menu, self.cart)
        self.wait_window(menu_popup)

    def view_cart(self):
        cart_view = CartViewPopup(self, self.cart)
        self.wait_window(cart_view)

    def checkout(self):
        validation = self.order_placement.validate_order()
        if not validation["success"]:
            messagebox.showerror("Error", validation["message"])
            return
        checkout_popup = CheckoutPopup(self, self.order_placement)
        self.wait_window(checkout_popup)


class AddItemPopup(tk.Toplevel):
    def __init__(self, master, menu, cart):
        super().__init__(master)
        self.title("Add Item to Cart")
        self.menu = menu
        self.cart = cart

        tk.Label(self, text="Select an item to add to cart:").pack(pady=10)
        self.item_var = tk.StringVar()
        self.item_var.set(self.menu.available_items[0] if self.menu.available_items else "")
        tk.OptionMenu(self, self.item_var, *self.menu.available_items).pack(pady=5)

        tk.Label(self, text="Quantity:").pack()
        self.qty_entry = tk.Entry(self)
        self.qty_entry.insert(0, "1")
        self.qty_entry.pack(pady=5)
        tk.Button(self, text="Add to Cart", command=self.add_to_cart).pack(pady=10)

    def add_to_cart(self):
        # ✅ Prevent crash or negative/invalid quantities
        try:
            item = self.item_var.get().strip()
            qty = int(self.qty_entry.get().strip())
            if qty <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Quantity", "Please enter a positive whole number.")
            return

        price = 10.0
        msg = self.cart.add_item(item, price, qty)
        messagebox.showinfo("Cart", msg)
        self.destroy()


class CartViewPopup(tk.Toplevel):
    def __init__(self, master, cart):
        super().__init__(master)
        self.title("Cart Items")

        items = cart.view_cart()
        if not items:
            tk.Label(self, text="Your cart is empty").pack(pady=20)
        else:
            for i in items:
                tk.Label(self, text=f"{i['name']} x{i['quantity']} = ${i['subtotal']:.2f}").pack()


class CheckoutPopup(tk.Toplevel):
    def __init__(self, master, order_placement):
        super().__init__(master)
        self.title("Checkout")
        self.order_placement = order_placement

        order_data = order_placement.proceed_to_checkout()
        tk.Label(self, text="Review your order:", font=("Arial", 12)).pack(pady=10)
        for item in order_data["items"]:
            tk.Label(self, text=f"{item['name']} x{item['quantity']} = ${item['subtotal']:.2f}").pack()

        total = order_data["total_info"]
        tk.Label(self, text=f"Subtotal: ${total['subtotal']:.2f}").pack()
        tk.Label(self, text=f"Tax: ${total['tax']:.2f}").pack()
        tk.Label(self, text=f"Delivery Fee: ${total['delivery_fee']:.2f}").pack()
        tk.Label(self, text=f"Total: ${total['total']:.2f}").pack()
        tk.Label(self, text=f"Delivery Address: {order_data['delivery_address']}").pack(pady=5)

        tk.Label(self, text="Payment Method:").pack(pady=5)
        self.payment_method = tk.StringVar()
        self.payment_method.set("credit_card")
        tk.Radiobutton(self, text="Credit Card", variable=self.payment_method, value="credit_card").pack()
        tk.Radiobutton(self, text="Paypal", variable=self.payment_method, value="paypal").pack()

        tk.Label(self, text="For credit card enter a 16-digit card number:").pack(pady=5)
        self.card_entry = tk.Entry(self)
        self.card_entry.insert(0, "1234567812345678")
        self.card_entry.pack(pady=5)
        tk.Button(self, text="Confirm Order", command=self.confirm_order).pack(pady=10)

    def confirm_order(self):
        # Use PaymentProcessing for secure payment validation
        total_amount = self.order_placement.cart.calculate_total()["total"]
        processor = PaymentProcessing()
        method = self.payment_method.get()

        if method == "credit_card":
            payment_details = {
                "card_number": self.card_entry.get().strip(),
                "expiry_date": "12/25",
                "cvv": "123",
            }
        else:
            payment_details = {"paypal_token": "demo"}

        result_msg = processor.process_payment(
            order={"total_amount": total_amount},
            payment_method=method,
            payment_details=payment_details
        )

        if not result_msg.startswith("Payment successful"):
            messagebox.showerror("Payment Error", result_msg)
            return

        result = self.order_placement.confirm_order(PaymentMethod())
        if result["success"]:
            messagebox.showinfo(
                "Order Confirmed",
                f"Order ID: {result['order_id']}\nEstimated Delivery: {result['estimated_delivery']}"
            )
            self.destroy()
        else:
            messagebox.showerror("Error", result["message"])
            
if __name__ == "__main__":
    app = Application()
    app.mainloop()
