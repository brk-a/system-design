# Adapter Design Pattern in Python

## WTF is the adapter design pattern?

The Adapter Design Pattern is a structural pattern that allows incompatible interfaces to work together. It is used to *"adapt"* one interface to another, that is, make it easier to integrate new systems with existing ones.

### Concepts

- **Adapter** &rarr; Converts one interface to another.
- **Target** &rarr; The interface that clients expect.
- **Adaptee** &rarr; The class that needs to be adapted.
- **Client** &rarr; The class that uses the Target interface.

The Adapter pattern allows for changing the interface of a class without modifying the class itself. It is particularly useful when you need to work with third-party libraries or existing classes that cannot be modified.

## Example 1: Simple Adapter Example

### Scenario:
A system that works with a legacy payment gateway that has a different interface from what the current system requires. You need an adapter to bridge the gap between the old and new system.

### Code:

```python
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
```

### Explanation:
- **LegacyPaymentGateway** is the existing class with the `old_payment_method`.
- **PaymentProcessor** is the new interface our system expects.
- **PaymentAdapter** adapts `LegacyPaymentGateway` to the `PaymentProcessor` interface.
- **client_code** is the client that uses the `PaymentProcessor` interface.

When you run this code, the output will be:
```
Adapting to new payment method...
Processing payment of 100 using legacy system...
```

## Example 2: More Advanced Adapter

### Scenario:
You are working on an application where you need to fetch data from different sources each with its own interface. We’ll adapt these interfaces using the Adapter pattern.

### Code:

```python
# Adaptee 1: Old Database
class OldDatabase:
    def fetch_data_from_old_system(self):
        return "Data from Old Database"

# Adaptee 2: New API
class NewAPI:
    def get_data_from_new_api(self):
        return "Data from New API"

# Target: Unified data fetching interface
class DataFetcher:
    def fetch_data(self):
        pass

# Adapter 1: Adapter for OldDatabase
class OldDatabaseAdapter(DataFetcher):
    def __init__(self, old_db: OldDatabase):
        self.old_db = old_db
    
    def fetch_data(self):
        print("Fetching data using Old Database adapter...")
        return self.old_db.fetch_data_from_old_system()

# Adapter 2: Adapter for NewAPI
class NewAPIAdapter(DataFetcher):
    def __init__(self, new_api: NewAPI):
        self.new_api = new_api
    
    def fetch_data(self):
        print("Fetching data using New API adapter...")
        return self.new_api.get_data_from_new_api()

# Client code
def client_code(data_fetcher: DataFetcher):
    data = data_fetcher.fetch_data()
    print(f"Fetched Data: {data}")

# Using the adapters
old_db = OldDatabase()
new_api = NewAPI()

old_db_adapter = OldDatabaseAdapter(old_db)
new_api_adapter = NewAPIAdapter(new_api)

client_code(old_db_adapter)
client_code(new_api_adapter)
```

### Explanation:
- **OldDatabase** and **NewAPI** are two different data sources each with its own interface.
- **DataFetcher** is the interface that the client code expects.
- **OldDatabaseAdapter** and **NewAPIAdapter** adapt the legacy database and new API to the unified interface.

The output will be:
```
Fetching data using Old Database adapter...
Fetched Data: Data from Old Database
Fetching data using New API adapter...
Fetched Data: Data from New API
```

### Key Points:
- The Adapter pattern allows different interfaces to be used interchangeably without modifying the existing codebase.
- In this example, we adapted two different systems (an old database and a new API) to the same `DataFetcher` interface.

## When to Use the Adapter Pattern

- **Integration with third-party libraries**: If you need to integrate with a library that has an incompatible interface.
- **Working with legacy systems**: If you're maintaining legacy systems that cannot be changed but need to integrate with new systems.
- **Handling multiple interfaces**: When you have a variety of systems that need to be handled through a common interface.

## Conclusion

The Adapter Design Pattern is a useful way to integrate incompatible systems and interface with them in a consistent way. It is particularly beneficial when dealing with legacy code or third-party libraries that cannot be modified. The Adapter pattern provides a way to adapt these systems to your needs without breaking the existing codebase.

---
**Advantages:**
- Provides flexibility to work with different systems.
- Allows easier integration without modifying existing systems.

**Disadvantages:**
- Can introduce additional complexity if overused.
- May cause inefficiency if there are many adapters for different components.

---

### Further Reading

- [Design Patterns: Elements of Reusable Object-Oriented Software](https://www.amazon.com/Design-Patterns-Elements-Reusable-Object-Oriented/dp/0201633612)
- [Adapter Pattern on Wikipedia](https://en.wikipedia.org/wiki/Adapter_pattern)


### How to Present:
1. **Start with the basics**: Explain what the Adapter pattern is and why it’s useful.
2. **Introduce the simple example**: Walk through the first example of adapting a legacy system to a new system.
3. **Show the advanced example**: Use the second example to demonstrate how multiple adapters can be used in a more complex real-world scenario.
4. **Discuss when to use the Adapter pattern**: Explain the scenarios where it’s beneficial.
5. **Conclude**: Summarise the advantages and disadvantages of the pattern and encourage questions.
