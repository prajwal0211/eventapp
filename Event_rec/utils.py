import hashlib

def hash_password(password):
    # Use a secure hash function for passwords
    return hashlib.sha256(password.encode()).hexdigest()
