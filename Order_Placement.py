from unittest import mock  # may still be needed in other test files, optional here.

# ---------------------- CartItem Class ----------------------
class CartItem:
    def __init__(self, name, price, quantity):
        self.name = name
        self.price = price
        self.quantity = quantity

    def update_quantity(self, new_quantity):
        self.quantity = new_quantity

    def get_subtotal(self):
        return self.price * self.quantity


# ---------------------- Cart Class ----------------------
class Cart:
    def __init__(self):
        self.items = []

    def add_item(self, name, price, quantity):
        for item in self.items:
            if item.name == name:
                item.update_quantity(item.quantity + quantity)
                return f"Updated {name} quantity to {item.quantity}"

        new_item = CartItem(name, price, quantity)
        self.items.append(new_item)
        return f"Added {name} to cart"

    def remove_item(self, name):
        self.items = [item for item in self.items if item.name != name]
        return f"Removed {name} from cart"

    def update_item_quantity(self, name, new_quantity):
        for item in self.items:
            if item.name == name:
                item.update_quantity(new_quantity)
                return f"Updated {name} quantity to {new_quantity}"
        return f"{name} not found in cart"

    def calculate_total(self):
        subtotal = sum(item.get_subtotal() for item in self.items)
        tax = subtotal * 0.10
        delivery_fee = 5.00
        total = subtotal + tax + delivery_fee
        return {
            "subtotal": subtotal,
            "tax": tax,
            "delivery_fee": delivery_fee,
            "total": total
        }

    def view_cart(self):
        return [
            {"name": item.name, "quantity": item.quantity, "subtotal": item.get_subtotal()}
            for item in self.items
        ]


# ---------------------- OrderPlacement Class ----------------------
class OrderPlacement:
    def __init__(self, cart, user_profile, restaurant_menu):
        self.cart = cart
        self.user_profile = user_profile
        self.restaurant_menu = restaurant_menu

    def validate_order(self):
        if not self.cart.items:
            return {"success": False, "message": "Cart is empty"}

        for item in self.cart.items:
            if not self.restaurant_menu.is_item_available(item.name):
                return {"success": False, "message": f"{item.name} is not available"}

        return {"success": True, "message": "Order is valid"}

    def proceed_to_checkout(self):
        total_info = self.cart.calculate_total()
        return {
            "items": self.cart.view_cart(),
            "total_info": total_info,
            "delivery_address": self.user_profile.delivery_address,
        }

    def confirm_order(self, payment_method):
        if not self.validate_order()["success"]:
            return {"success": False, "message": "Order validation failed"}

        payment_success = payment_method.process_payment(self.cart.calculate_total()["total"])

        if payment_success:
            return {
                "success": True,
                "message": "Order confirmed",
                "order_id": "ORD123456",
                "estimated_delivery": "45 minutes"
            }

        return {"success": False, "message": "Payment failed"}


# ---------------------- Supporting Classes ----------------------
class PaymentMethod:
    def process_payment(self, amount):
        return amount > 0


class UserProfile:
    def __init__(self, delivery_address):
        self.delivery_address = delivery_address


class RestaurantMenu:
    def __init__(self, available_items):
        self.available_items = available_items

    def is_item_available(self, item_name):
        return item_name in self.available_items
