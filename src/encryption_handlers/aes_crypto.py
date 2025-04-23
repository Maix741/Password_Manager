import os

from base64 import b64encode, b64decode
from Crypto.Cipher import AES


class AESCrypto:
    def __init__(self) -> None:
        self.enc_dec_method = "utf-8"

    def encrypt(self, str_to_encrypt: str, str_key: str, salt: bytes) -> str:
        try:
            aes_object = AES.new(str_key.encode("utf-8"), AES.MODE_CFB, salt)

            encryption: bytes = aes_object.encrypt(str_to_encrypt.encode(self.enc_dec_method))
            encryption_b64: str = b64encode(encryption).decode(self.enc_dec_method)

            return encryption_b64

        except ValueError as value_error:
            if value_error.args[0] == "IV must be 16 bytes long":
                raise ValueError("Encryption Error: SALT must be 16 characters long")
            elif value_error.args[0] == "AES key must be either 16, 24, or 32 bytes long":
                raise ValueError("Encryption Error: Encryption key must be either 16, 24, or 32 characters long")
            raise ValueError(value_error)

    def decrypt(self, encrypted_str: str, str_key: str, salt: bytes) -> str:
        try:
            aes_object = AES.new(str_key.encode(self.enc_dec_method), AES.MODE_CFB, salt)
            encoded_str: bytes = b64decode(encrypted_str.encode(self.enc_dec_method))

            decrypted_str: bytes = aes_object.decrypt(encoded_str)
            decoded_str: str = decrypted_str.decode(self.enc_dec_method)

            return decoded_str

        except ValueError as value_error:
            if value_error.args[0] == "IV must be 16 bytes long":
                raise ValueError("Decryption Error: SALT must be 16 characters long")
            elif value_error.args[0] == "AES key must be either 16, 24, or 32 bytes long":
                raise ValueError("Decryption Error: Encryption key must be either 16, 24, or 32 characters long")
            else:
                raise ValueError(value_error)


if __name__ == "__main__":
    # test case | example use case #
    test_crypt: AESCrypto = AESCrypto()
    test_text: str = "Lorem ipsum dolor sit amet"
    test_key: str = "MyKey4TestingThs"
    salt: bytes = os.urandom(16)

    test_enc_text: str = test_crypt.encrypt(test_text, test_key, salt)
    test_dec_text: str = test_crypt.decrypt(test_enc_text, test_key, salt)

    print(f"Encrypted:{test_enc_text}  Decrypted:{test_dec_text}")
