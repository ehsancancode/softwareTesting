import unittest
from unittest import mock
from Order_Placement import (
    Cart,
    OrderPlacement,
    PaymentMethod,
    UserProfile,
    RestaurantMenu,
)

class TestOrderPlacement(unittest.TestCase):

    def setUp(self):
        self.restaurant_menu = RestaurantMenu(available_items=["Burger", "Pizza", "Salad"])
        self.user_profile = UserProfile(delivery_address="123 Main St")
        self.cart = Cart()
        self.order = OrderPlacement(self.cart, self.user_profile, self.restaurant_menu)

    def test_validate_order_empty_cart(self):
        result = self.order.validate_order()
        self.assertFalse(result["success"])
        self.assertEqual(result["message"], "Cart is empty")

    def test_validate_order_item_not_available(self):
        self.cart.add_item("Pasta", 15.99, 1)
        result = self.order.validate_order()
        self.assertFalse(result["success"])
        self.assertEqual(result["message"], "Pasta is not available")

    def test_validate_order_success(self):
        self.cart.add_item("Burger", 8.99, 2)
        result = self.order.validate_order()
        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "Order is valid")

    def test_confirm_order_success(self):
        self.cart.add_item("Pizza", 12.99, 1)
        payment_method = PaymentMethod()
        result = self.order.confirm_order(payment_method)
        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "Order confirmed")
        self.assertEqual(result["order_id"], "ORD123456")

    def test_confirm_order_failed_payment(self):
        self.cart.add_item("Pizza", 12.99, 1)
        payment_method = PaymentMethod()

        with mock.patch.object(payment_method, 'process_payment', return_value=False):
            result = self.order.confirm_order(payment_method)
            self.assertFalse(result["success"])
            self.assertEqual(result["message"], "Payment failed")
#NEW CODE ADDED BY JIMMY BELOW
class StubSuccessfulPayment(PaymentMethod):
    def process_payment(self, amount):
        return True

class StubFailedPayment(PaymentMethod):
    def process_payment(self, amount):
        return False

class TestOrderPlacementWithStubs(unittest.TestCase):
    def setUp(self):
        self.cart = Cart()
        self.cart.add_item("Pizza", 12.99, 1)
        self.user_profile = UserProfile(delivery_address="123 Main St")
        self.menu = RestaurantMenu(available_items=["Pizza"])
        self.order = OrderPlacement(self.cart, self.user_profile, self.menu)

    def test_confirm_order_with_successful_payment_stub(self):
        successful_payment_stub = StubSuccessfulPayment()
        result = self.order.confirm_order(successful_payment_stub)
        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "Order confirmed")

    def test_confirm_order_with_failed_payment_stub(self):
        failed_payment_stub = StubFailedPayment()
        result = self.order.confirm_order(failed_payment_stub)
        self.assertFalse(result["success"])
        self.assertEqual(result["message"], "Payment failed")


class TestOrderPlacementInteractions(unittest.TestCase):
    def setUp(self):
        self.cart = Cart()
        self.user_profile = UserProfile(delivery_address="123 Main St")
        self.menu = RestaurantMenu(available_items=["Burger"])
        self.order = OrderPlacement(self.cart, self.user_profile, self.menu)

    def test_confirm_order_calls_payment_with_correct_total(self):
        self.cart.add_item("Burger", 10.00, 2) 
        
        expected_total = self.cart.calculate_total()["total"]
        self.assertEqual(expected_total, 27.00) 

        mock_payment_method = mock.MagicMock(spec=PaymentMethod)
        
        mock_payment_method.process_payment.return_value = True

        self.order.confirm_order(mock_payment_method)

        mock_payment_method.process_payment.assert_called_once()
        
        mock_payment_method.process_payment.assert_called_with(expected_total)


if __name__ == "__main__":
    unittest.main()
