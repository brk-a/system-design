# Decorator Design Pattern

## Principles of the Decorator Pattern

- **Open/Closed Principle**: Classes should be open for extension but closed for modification. Decorators allow us to extend functionality without changing the original code.
- **Composition over Inheritance**: Instead of creating subclasses to add behaviour, decorators wrap existing objects enabling behaviour to be added dynamically.
- **Single Responsibility Principle**: Decorators can handle specific responsibilities (like logging, caching, etc.) without overloading the original class.

---

## WTF is the Decorator Pattern?

-  The decorator pattern allows us to add new functionality to an object dynamically without altering its structure.
- **How it works**: You wrap an object in another object (the decorator) which adds additional behaviour to the wrapped object.

---

## Basic Example - Adding Milk to Coffee

1. **Base Object**: A simple `Coffee` class.
2. **Decorator**: A `MilkDecorator` that adds milk to the coffee cost.

    ```python
        class Coffee:
            def cost(self):
                return 5

        class CoffeeDecorator:
            def __init__(self, coffee):
                self._coffee = coffee
            
            def cost(self):
                return self._coffee.cost()

        class MilkDecorator(CoffeeDecorator):
            def cost(self):
                return self._coffee.cost() + 2

        black_coffee = Coffee()
        print(f'Black coffee cost: {black_coffee.cost()}')

        milk_coffee = MilkDecorator(black_coffee)
        print(f'Milk coffee cost: {milk_coffee.cost()}')
    ```

**Output**:
    ```plaintext
        Black coffee cost: 5
        Milk coffee cost: 7
    ```

---

## Example 2 - Logging Decorator

1. **Base Function**: A function to process payments.
2. **Decorator**: A `LoggerDecorator` that logs the execution time.

    ```python
        import time

        class LoggerDecorator:
            def __init__(self, wrapped):
                self._wrapped = wrapped
            
            def __call__(self, *args, **kwargs):
                start_time = time.time()
                result = self._wrapped(*args, **kwargs)
                end_time = time.time()
                print(f'Execution time: {end_time - start_time:.4f} seconds')
                return result

        def process_payment(amount):
            time.sleep(1)
            return f'Payment of {amount} processed'

        decorated_payment = LoggerDecorator(process_payment)
        decorated_payment(100)
    ```

---

## Example 3 - Caching Decorator

1. **Base Function**: A function to fetch user data.
2. **Decorator**: A `CacheDecorator` that caches the result to avoid duplicate database calls.

    ```python
        class CacheDecorator:
            def __init__(self, wrapped):
                self._wrapped = wrapped
                self.cache = {}

            def __call__(self, *args, **kwargs):
                if args in self.cache:
                    print("Returning cached result")
                    return self.cache[args]
                result = self._wrapped(*args, **kwargs)
                self.cache[args] = result
                return result

        def get_user_from_db(user_id):
            print("Fetching from DB...")
            return f'User {user_id} details'

        cached_user = CacheDecorator(get_user_from_db)
        print(cached_user(1))  # Fetch from DB
        print(cached_user(1))  # Return from cache
    ```

---

## Other Examples

**Scenario**: Enhancing functionality without modifying the core logic.

1. **Security Decorator**: To ensure security checks (e.g., admin role) are done before transferring funds.
2. **Interest Calculation**: Dynamically apply interest to an account balance without altering core account logic.

---

## Security Decorator Example

    ```python
        class SecurityDecorator:
            def __init__(self, wrapped):
                self._wrapped = wrapped
            
            def __call__(self, *args, **kwargs):
                user = kwargs.get('user')
                print(f'Security check for {user}')
                return self._wrapped(*args, **kwargs)

        def transfer_funds(amount, user):
            print(f'Transferring {amount} to another account')

        secure_transfer = SecurityDecorator(transfer_funds)
        secure_transfer(1000, user="admin")
    ```

---

## Interest Calculation Example

    ```python
        class InterestDecorator:
            def __init__(self, wrapped):
                self._wrapped = wrapped
            
            def __call__(self, *args, **kwargs):
                amount = args[0]
                rate = kwargs.get('rate', 0.05)
                interest = amount * rate
                total = amount + interest
                print(f'Added {interest} interest. Total balance: {total}')
                return total

        def account_balance(balance):
            return balance

        account_with_interest = InterestDecorator(account_balance)
        account_with_interest(1000, rate=0.03)
    ```

---

## Strengths of the Decorator Pattern

- **Extensibility**: Easily extend functionality without modifying existing code.
- **Flexibility**: Stack decorators to combine multiple behaviours (logging, caching, security, etc.).
- **Separation of Concerns**: Keep code clean by separating concerns (e.g., logging in one decorator, caching in another).

---

## Weaknesses of the Decorator Pattern

- **Complexity with Many Layers**: Too many stacked decorators can make the code hard to follow and debug.
- **Tight Coupling**: The decorator and the wrapped object can become tightly coupled, which may limit flexibility in some cases.
- **Overuse**: Excessive use of decorators can lead to over-engineering and overly complex solutions.

---

## When TF to Use the Decorator Pattern

- When you need to **extend functionality** of an object without changing its class.
- When you need to **add cross-cutting concerns** (e.g. logging, security, etc.) to multiple objects.
- When you want to **combine multiple behaviours** in a flexible and reusable way.

---

## When Not to Use the Decorator Pattern

- **If the Decorators Make Code Harder to Understand**: If you're stacking too many decorators, it can make the flow of the code difficult to follow, especially if the decorators are not well-named or documented.
- **When Simpler Alternatives Exist**: If adding functionality can be achieved by simple inheritance, composition, or other patterns, the decorator might be overkill.
- **In Performance-Critical Applications**: Decorators can add overhead, particularly when used excessively or when they wrap expensive operations. If performance is a critical concern, this pattern may not be ideal.
- **If You Cannot Control the Wrapping Order**: The order in which decorators are applied is important. If there’s no clear control over the order of wrapping, it could lead to unexpected results or behaviours.

---

## Conclusion

- The **Decorator Pattern** provides a clean and flexible way to add functionality to objects dynamically.
- It allows **extension without modification**; it maintains open/closed design principles.
- Great for managing concerns like logging, caching, and security in a maintainable way.
- Always consider the potential complexity when stacking decorators.

---
