import os
import psycopg2
import logging
from fastapi import FastAPI
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from datetime import datetime, timezone
from OpenSSL import SSL

BASE_FOLDER = os.path.dirname(os.path.abspath(__file__))

logging.basicConfig(filename=os.path.join(BASE_FOLDER, "error.log"), level=logging.ERROR, 
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.conn = None
        self.cur = None

    def connect(self):
        try:
            self.conn = psycopg2.connect(
                dbname='postgres',
                user='postgres',
                password='password',
                host='db'
            )
            self.cur = self.conn.cursor()
        except Exception as e:
            logger.error(f"Failed to connect to database: {str(e)}")

    def close(self):
        if self.cur is not None:
            self.cur.close()
        if self.conn is not None:
            self.conn.close()

    def create_table(self):
        try:
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS computers (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255),
                    update_status BOOLEAN,
                    reboot_required BOOLEAN
                )
            """)
            self.conn.commit()
        except Exception as e:
            logger.error(f"Failed to create table: {str(e)}")

    def insert_computer(self, name, update_status, reboot_required):
        try:
            self.cur.execute("""
                INSERT INTO computers (name, update_status, reboot_required)
                VALUES (%s, %s, %s)
            """, (name, update_status, reboot_required))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Failed to insert computer: {str(e)}")

    def get_computers(self):
        try:
            self.cur.execute("SELECT * FROM computers")
            return self.cur.fetchall()
        except Exception as e:
            logger.error(f"Failed to get computers: {str(e)}")

app = FastAPI()
app.add_middleware(HTTPSRedirectMiddleware)

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

@app.get("/get-computers")
def get_computers():
    try:
        db = Database()
        db.connect()
        computers = db.get_computers()
        db.close()
        return computers
    except Exception as e:
        logger.error(str(e))
        return {"error": "An error occurred while getting the computers"}

@app.post("/add-computer")
def add_computer(name: str, update_status: bool, reboot_required: bool):
    try:
        db = Database()
        db.connect()
        db.insert_computer(name, update_status, reboot_required)
        db.close()
        return {"message": "Computer added successfully"}
    except Exception as e:
        logger.error(str(e))
        return {"error": "An error occurred while adding the computer"}

if __name__ == "__main__":
    try:
        if __name__ == "__main__":
            os.system(f"gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 --certfile={cert_file} --keyfile={key_file} --ciphers=ECDHE+AESGCM server:app")
    except Exception as e:
        print(f"An error occurred: {e}")