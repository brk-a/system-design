### **Decorators vs Decorator design pattern**
**decorator** &rarr;  a function that takes another function or method as an argument and extends or alters its behaviour without explicitly modifying its code. It is a high-level concept in Python commonly used to modify or enhance the functionality of functions or methods in a clean and readable way.

* example: simple decorator

    ```python
    def my_decorator(func):
        def wrapper():
            print("Before the function")
            func()
            print("After the function")
        return wrapper

    @my_decorator
    def say_hello():
        print("Hello!")

    say_hello()
    ```

    **Output:**
    ```
    Before the function
    Hello!
    After the function
    ```

#### Key points:
- **Syntax:** Decorators use the `@decorator_name` syntax.
- **Purpose:** Primarily used to modify the behaviour of functions or methods (e.g. logging, access control, timing).
- **Scope:** They are more focused on enhancing functions without changing their original code.

**decorator design pattern** &rarr; a structural pattern from object-oriented design that allows you to dynamically add functionality to an object at runtime without affecting other objects of the same class. It involves creating a set of decorator classes that are used to wrap concrete components.

* In Python, you can implement the decorator pattern by defining a base class and then wrapping it with various *"decorator"* classes to add or override behaviour.

* example: milk, coffee and sugar

    ```python
    class Coffee:
        def cost(self):
            return 5

    class MilkDecorator:
        def __init__(self, coffee):
            self._coffee = coffee

        def cost(self):
            return self._coffee.cost() + 2

    class SugarDecorator:
        def __init__(self, coffee):
            self._coffee = coffee

        def cost(self):
            return self._coffee.cost() + 1

    coffee = Coffee()
    print("Cost of black coffee:", coffee.cost())

    milk_coffee = MilkDecorator(coffee)
    print("Cost of milk coffee:", milk_coffee.cost())

    sugar_milk_coffee = SugarDecorator(milk_coffee)
    print("Cost of sugar milk coffee:", sugar_milk_coffee.cost())
    ```

    **Output:**
    ```
    Cost of coffee: 5
    Cost of milk coffee: 7
    Cost of sugar milk coffee: 8
    ```

#### Key points:
- **Pattern:** The decorator pattern is part of design patterns so it is more of an object-oriented solution.
- **Purpose:** It allows adding new behaviour to objects without altering the original object.
- **Scope:** It works with classes and objects modifying their behaviour dynamically at runtime.

### **Key Differences**
1. **Purpose:**
   - **Decorators (Python)**: A language feature to modify functions or methods.
   - **Decorator Pattern**: A design pattern used to modify or extend the behavior of objects dynamically.

2. **Usage:**
   - **Decorators (Python)**: Applied to functions or methods, typically used for cross-cutting concerns like logging or caching.
   - **Decorator Pattern**: Applied to objects to add new behavior without modifying the original object class.

3. **Structure:**
   - **Decorators (Python)**: Function-based, use closures.
   - **Decorator Pattern**: Class-based; relies on composition and inheritance.
### **Long Story Short**
- decorators in Python are a more straightforward and syntactically clean way to enhance functions; decorator design pattern provides a more formal structure for dynamically adding behaviour to objects in an object-oriented way.