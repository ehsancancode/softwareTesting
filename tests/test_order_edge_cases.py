import unittest
from Order_Placement import Cart, OrderPlacement, UserProfile, RestaurantMenu, PaymentMethod

class TestOrderEdgeCases(unittest.TestCase):
    def setUp(self):
        self.menu = RestaurantMenu(["Pizza"])
        self.user = UserProfile("123 Street")
        self.cart = Cart()
        self.order = OrderPlacement(self.cart, self.user, self.menu)

    # NEW TEST: empty cart validation
    def test_validate_order_empty_cart(self):
        res = self.order.validate_order()
        self.assertFalse(res["success"])

    # NEW TEST: unavailable item
    def test_validate_order_unavailable_item(self):
        self.cart.add_item("Burger", 10.0, 1)
        res = self.order.validate_order()
        self.assertFalse(res["success"])
        self.assertIn("not available", res["message"])

    # NEW TEST: failed payment
    def test_confirm_order_failed_payment(self):
        self.cart.add_item("Pizza", 10.0, 1)
        fake_payment = PaymentMethod()
        fake_payment.process_payment = lambda order: False
        res = self.order.confirm_order(fake_payment)
        self.assertFalse(res["success"])
