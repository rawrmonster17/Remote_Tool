from fastapi import FastAPI
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from OpenSSL import SSL
import os
from datetime import datetime, timezone


app = FastAPI()
app.add_middleware(HTTPSRedirectMiddleware)
BASE_FOLDER = "/app"

# Check if the certificate file exists
cert_file = os.path.join(BASE_FOLDER, "cert.pem")
key_file = os.path.join(BASE_FOLDER, "key.pem")

ip_address = "192.168.1.201"

if not os.path.exists(cert_file) or not os.path.exists(key_file):
    # Create a self-signed certificate using OpenSSL
    os.system(f"openssl req -x509 -newkey rsa:4096 -nodes -out {cert_file} -keyout {key_file} -days 365 -subj '/CN={ip_address}'")
else:
    # Check if the certificate is within 3 months of expiring
    with open(cert_file, 'rt') as f:
        cert = x509.load_pem_x509_certificate(f.read().encode(), default_backend())
    expiration_date = cert.not_valid_after_utc
    remaining_days = (expiration_date - datetime.utcnow().replace(tzinfo=timezone.utc)).days
    if remaining_days <= 90:
        # Create a new certificate
        os.system(f"openssl req -x509 -newkey rsa:4096 -nodes -out {cert_file} -keyout {key_file} -days 365 -subj '/CN={ip_address}'")

# Load the SSL context with the certificate and private key
ssl_context = SSL.Context(SSL.SSLv23_METHOD)
ssl_context.use_certificate_file(cert_file)
ssl_context.use_privatekey_file(key_file)
# Disable SSLv2, SSLv3, TLSv1, and TLSv1.1
ssl_context.set_options(SSL.OP_NO_SSLv2)
ssl_context.set_options(SSL.OP_NO_SSLv3)
ssl_context.set_options(SSL.OP_NO_TLSv1)
ssl_context.set_options(SSL.OP_NO_TLSv1_1)

@app.get("/")
def read_root():
    return {"Hello, tresspassser"}

if __name__ == "__main__":
    try:
        if __name__ == "__main__":
            os.system(f"gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 --certfile={cert_file} --keyfile={key_file} --ciphers=ECDHE+AESGCM server:app")
    except Exception as e:
        print(f"An error occurred: {e}")