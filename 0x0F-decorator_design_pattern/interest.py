#!/usr/bin/env python


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

if __name__ == '__main__':
    account_with_interest = InterestDecorator(account_balance)
    account_with_interest(1000, rate=0.03)
