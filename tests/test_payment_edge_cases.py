import unittest
from Payment_Processing import PaymentProcessing

class TestPaymentEdgeCases(unittest.TestCase):
    def setUp(self):
        self.pp = PaymentProcessing()

    # NEW TEST: invalid gateway
    def test_invalid_gateway(self):
        with self.assertRaises(ValueError):
            self.pp.validate_payment_method("crypto", {"card_number": "1234"})

    # NEW TEST: card decline mock
    def test_declined_card_gateway(self):
        details = {"card_number": "1111222233334444", "expiry_date": "12/25", "cvv": "123"}
        res = self.pp.mock_payment_gateway("credit_card", details, 20)
        self.assertEqual(res["status"], "failure")
