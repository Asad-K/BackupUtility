"""
source: https://eli.thegreenplace.net/2010/06/25/aes-encryption-of-files-in-python-with-pycrypto/
minor changes for compatibility with 3.7
"""
import os
import struct
import hashlib
from Crypto.Cipher import AES
from Crypto import Random


class Crypto:

    def __init__(self, password):
        self.__dk = self.__derive_key(password)

    @staticmethod
    def __derive_key(password):
        """
        derives cryptographic key using pbkdf2 key derivation scheme
        salt = sha3_256 digest of password string, 16 bytes as recommended
        """
        salt = hashlib.sha3_256(password.encode()).digest()
        return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)

    def encrypt_file(self, in_filename, out_filename=None, chunksize=64 * 1024):

        """ Encrypts a file using AES (CBC mode) with the
            given key.

            key:
                The encryption key - a string that must be
                either 16, 24 or 32 bytes long. Longer keys
                are more secure.

            in_filename:
                Name of the input file

            out_filename:
                If None, '<in_filename>.enc' will be used.

            chunksize:
                Sets the size of the chunk which the function
                uses to read and encrypt the file. Larger chunk
                sizes can be faster for some files and machines.
                chunksize must be divisible by 16.
        """
        if not out_filename:
            out_filename = in_filename + '.locked'

        iv = Random.new().read(AES.block_size)
        encryptor = AES.new(self.__dk, AES.MODE_CBC, iv)
        fsize = os.path.getsize(in_filename)

        with open(in_filename, 'rb') as infile:
            with open(out_filename, 'wb+') as outfile:
                outfile.write(struct.pack('<Q', fsize))
                outfile.write(iv)

                while True:
                    chunk = infile.read(chunksize)
                    if len(chunk) == 0:
                        break
                    elif len(chunk) % 16 != 0:
                        chunk += b' ' * (16 - len(chunk) % 16)

                    outfile.write(encryptor.encrypt(chunk))
                outfile.seek(0)
        return outfile.name

    def decrypt_file(self, in_filename, out_filename=None, chunksize=64 * 1024):
        """ Decrypts a file using AES (CBC mode) with the
            given key. Parameters are similar to encrypt_file,
            with one difference: out_filename, if not supplied
            will be in_filename without its last extension
            (i.e. if in_filename is 'aaa.zip.enc' then
            out_filename will be 'aaa.zip')
        """
        if out_filename is None:
            out_filename = os.path.splitext(in_filename)[0]

        with open(in_filename, 'rb') as infile:
            origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]

            iv = infile.read(16)

            decryptor = AES.new(self.__dk, AES.MODE_CBC, iv)

            with open(out_filename, 'wb') as outfile:

                while True:
                    chunk = infile.read(chunksize)
                    if len(chunk) == 0:
                        break
                    outfile.write(decryptor.decrypt(chunk))

                outfile.truncate(origsize)
