from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


def encrypt_AES_128(data, secret_key):
    key = secret_key.encode('utf-8')
    cipher = AES.new(key, AES.MODE_ECB)
    ciphertext = cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))
    return ciphertext.hex()


def decrypt_AES_128(data, secret_key):
    key = secret_key.encode('utf-8')
    cipher = AES.new(key, AES.MODE_ECB)
    decrypted_data = unpad(cipher.decrypt(bytes.fromhex(data)), AES.block_size)
    return decrypted_data.decode('utf-8')
