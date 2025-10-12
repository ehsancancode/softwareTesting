class PaymentProcessing:
    """
    Handles validation and processing of payments using supported gateways.
    """

    def __init__(self):
        """Initialize available payment gateways."""
        self.available_gateways = ["credit_card", "paypal"]

    def validate_payment_method(self, payment_method, payment_details):
        """
        Validates a selected payment method and its details.
        Raises ValueError if invalid.
        """
        if payment_method not in self.available_gateways:
            raise ValueError("Invalid payment method")

        if payment_method == "credit_card" and not self.validate_credit_card(payment_details):
            raise ValueError("Invalid credit card details")

        return True

    def validate_credit_card(self, details):
        """
        Basic validation for credit card details.
        """
        card_number = details.get("card_number", "")
        expiry_date = details.get("expiry_date", "")
        cvv = details.get("cvv", "")

        return len(card_number) == 16 and len(cvv) == 3

    def process_payment(self, order, payment_method, payment_details):
        """
        Processes a payment and returns a success/failure message.
        """
        try:
            self.validate_payment_method(payment_method, payment_details)
            payment_response = self.mock_payment_gateway(
                payment_method, payment_details, order["total_amount"]
            )

            if payment_response["status"] == "success":
                return "Payment successful, Order confirmed"
            else:
                return "Payment failed, please try again"

        except Exception as e:
            return f"Error: {str(e)}"

    def mock_payment_gateway(self, method, details, amount):
        """
        Mock payment gateway simulation.
        """
        # Simulate declined card
        if method == "credit_card" and details["card_number"] == "1111222233334444":
            return {"status": "failure", "message": "Card declined"}

        # Simulate success
        return {"status": "success", "transaction_id": "abc123"}
