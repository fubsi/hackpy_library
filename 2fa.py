import time
import pyotp
import qrcode

secret_key = "JBSWY3DPEHPK3PXP"  # This should be a base32 encoded string

uri = pyotp.totp.TOTP(secret_key).provisioning_uri(
    name='Fubsi',
    issuer_name='LibraryApp')

print(uri)


# # Qr code generation step
qrcode.make(uri).save("qrcode.png")

"""Verifying stage starts"""

totp = pyotp.TOTP(secret_key)

# verifying the code
while True:
  print(totp.verify(input(("Enter the Code : "))))