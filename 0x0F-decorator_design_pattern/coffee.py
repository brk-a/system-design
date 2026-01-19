#!/usr/bin/env python

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