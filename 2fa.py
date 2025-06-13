import time
import pyotp
import qrcode

secret_key = "THISISMYLIBRARYSECRET"  # This should be a base32 encoded string
# secret_key = pyotp.random_base32()  # Generate a random base32 secret key

totp = pyotp.TOTP(secret_key)

uri = totp.provisioning_uri(
    name='fubsi',
    issuer_name='LibraryApp')

print(uri)

# # Qr code generation step
qrcode.make(uri).save("qrcode.png")

"""Verifying stage starts"""
# verifying the code
while True:
  print("TOTP Code:", totp.now())
  print(totp.verify(input(("Enter the Code : "))))