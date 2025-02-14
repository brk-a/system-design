#!/usr/bin/env python3

# Adaptee: The legacy payment gateway
class LegacyPaymentGateway:
    def old_payment_method(self, amount):
        print(f"Processing payment of {amount} using legacy system...")

# Target: The interface that the current system expects
class PaymentProcessor:
    def process_payment(self, amount):
        pass

# Adapter: Adapts the legacy system to the new interface
class PaymentAdapter(PaymentProcessor):
    def __init__(self, legacy_gateway: LegacyPaymentGateway):
        self.legacy_gateway = legacy_gateway
    
    def process_payment(self, amount):
        print("Adapting to new payment method...")
        self.legacy_gateway.old_payment_method(amount)

# Client: The code that uses the Adapter
def client_code(payment_processor: PaymentProcessor, amount):
    payment_processor.process_payment(amount)

# Using the adapter
legacy_gateway = LegacyPaymentGateway()
adapter = PaymentAdapter(legacy_gateway)
client_code(adapter, 100)