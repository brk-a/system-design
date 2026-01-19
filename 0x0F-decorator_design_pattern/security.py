#!/usr/bin/env python

class SecurityDecorator:
    def __init__(self, wrapped):
        self._wrapped = wrapped
    
    def __call__(self, *args, **kwargs):
        user = kwargs.get('user')
        print(f'Security check for {user}')
        return self._wrapped(*args, **kwargs)

def transfer_funds(amount, user):
    print(f'Transferring {amount} to another account')

if __name__ == '__main__':
    secure_transfer = SecurityDecorator(transfer_funds)
    secure_transfer(1000, user="admin")