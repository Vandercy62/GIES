import secrets

if __name__ == "__main__":
    print("Nova SECRET_KEY gerada:")
    print(secrets.token_urlsafe(32))
