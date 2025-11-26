import random, string

def generate_product_sku():
    return ''.join(random.choices(string.digits, k=6))
