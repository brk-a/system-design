#!/usr/bin/env python

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

if __name__ == '__main__':
    decorated_payment = LoggerDecorator(process_payment)
    decorated_payment(100)