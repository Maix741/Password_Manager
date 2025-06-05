from cryptography.fernet import Fernet


class FernetCrypto:
    def __init__(self):
        self.enc_dec_method = "utf-8"

    def encrypt(self, str_to_encrypt: str, fernet_key: bytes) -> str:
        try:
            fernet_object = Fernet(fernet_key)
            bytes_to_encrypt: bytes = str_to_encrypt.encode(self.enc_dec_method)

            encryption_bytes: bytes = fernet_object.encrypt(bytes_to_encrypt)
            encryption_str: str = encryption_bytes.decode(self.enc_dec_method)

            return encryption_str

        except ValueError as value_error:
            raise ValueError(value_error)

    def decrypt(self, encrypted_str: str, fernet_key: bytes) -> str:
        try:
            fernet_object = Fernet(fernet_key)
            bytes_to_decrypt = encrypted_str.encode(self.enc_dec_method)

            decryption_bytes: bytes = fernet_object.decrypt(bytes_to_decrypt)
            decryption_str: str = decryption_bytes.decode(self.enc_dec_method)

            return decryption_str

        except ValueError as value_error:
            raise ValueError(value_error)


if __name__ == "__main__":
    # test case | example use case #
    test_crypt: FernetCrypto = FernetCrypto()
    test_text: str = "Lorem ipsum dolor sit amet"
    test_key: bytes = Fernet.generate_key()

    test_enc_text: str = test_crypt.encrypt(test_text, test_key)
    test_dec_text: str = test_crypt.decrypt(test_enc_text, test_key)

    print(f"Encrypted: {test_enc_text}  Decrypted: {test_dec_text}")
