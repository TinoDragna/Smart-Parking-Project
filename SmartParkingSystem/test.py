import pyotp
secret = pyotp.random_base32()
otp_uri = pyotp.totp.TOTP(secret).provisioning_uri(name="username", issuer_name="SecureApp")
