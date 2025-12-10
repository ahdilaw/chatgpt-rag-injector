import sys
import os
import time
import subprocess
import logging
import base64
import hashlib
import socket
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMessageBox
from OpenSSL import crypto

logging.basicConfig(level=logging.INFO)

def find_free_port():
    """Find an available port dynamically"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

def create_openssl_config():
    config_dir = Path(__file__).parent / "config"
    config_dir.mkdir(exist_ok=True)
    
    openssl_conf = config_dir / "openssl.cnf"
    if not openssl_conf.exists():
        minimal_config = """
[req]
default_bits = 2048
prompt = no
default_md = sha256
distinguished_name = req_distinguished_name
x509_extensions = v3_ca

[req_distinguished_name]
CN = Custom Proxy CA
O = Your Company
C = US

[v3_ca]
basicConstraints = critical,CA:TRUE
keyUsage = critical,keyCertSign,cRLSign
"""
        openssl_conf.write_text(minimal_config)
    
    return openssl_conf

def setup_certificates():
    logging.info("Setting up certificates...")
    openssl_conf = create_openssl_config()
    os.environ['OPENSSL_CONF'] = str(openssl_conf)
    
    cert_dir = Path(__file__).parent / "certificates"
    cert_dir.mkdir(exist_ok=True)
    
    ca_cert = cert_dir / "mitmproxy-ca.pem"
    ca_key = cert_dir / "mitmproxy-ca.key"
    
    if not ca_cert.exists() or not ca_key.exists():
        logging.info("Generating new CA certificate...")
        try:
            result = subprocess.run([
                "openssl", "req", "-new", "-x509", "-days", "3650",
                "-keyout", str(ca_key), "-out", str(ca_cert),
                "-nodes"
            ], check=True, capture_output=True, text=True, timeout=60)
            logging.info(f"OpenSSL output: {result.stdout}")
            logging.error(f"OpenSSL errors: {result.stderr}")
        except subprocess.TimeoutExpired:
            logging.error("OpenSSL command timed out")
            raise
        except subprocess.CalledProcessError as e:
            logging.error(f"OpenSSL command failed with error: {e.stderr}")
            raise
    
    logging.info("Certificates setup complete.")
    return ca_cert, ca_key

def compute_spki_hash(ca_cert_path):
    with open(ca_cert_path, 'rb') as f:
        cert_data = f.read()
    cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert_data)
    spki = crypto.dump_publickey(crypto.FILETYPE_ASN1, cert.get_pubkey())
    spki_hash = hashlib.sha256(spki).digest()
    spki_hash_b64 = base64.b64encode(spki_hash).decode('ascii')
    return spki_hash_b64

if __name__ == "__main__":
    logging.info("Starting application...")
    app = QApplication(sys.argv)
    
    try:
        # Dynamic port allocation
        proxy_port = find_free_port()
        print(f"🚀 Starting secure proxy on port: {proxy_port}")
        logging.info(f"Using dynamic proxy port: {proxy_port}")
        
        ca_cert, ca_key = setup_certificates()
        
        # Compute the SPKI hash
        spki_hash_b64 = compute_spki_hash(ca_cert)
        logging.info(f"SPKI Hash: {spki_hash_b64}")

        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (
            f"--proxy-server=127.0.0.1:{proxy_port} "
            f"--ignore-certificate-errors-spki-list={spki_hash_b64}"
        )
        
        logging.info("Importing ui.py and mitmproxy_integration.py...")
        try:
            from ui import MainWindow
            logging.info("Imported MainWindow successfully.")
        except Exception as e:
            logging.error(f"Error importing MainWindow: {e}")
            raise

        try:
            from mitmproxy_integration import MitmProxyThread
            logging.info("Imported MitmProxyThread successfully.")
        except Exception as e:
            logging.error(f"Error importing MitmProxyThread: {e}")
            raise

        logging.info("Imports successful.")
        
        print("⏳ Starting secure proxy server...")
        logging.info("Starting mitmproxy thread...")
        proxy_thread = MitmProxyThread(ca_cert, ca_key, proxy_port)
        proxy_thread.start()
        logging.info("mitmproxy thread started.")
        print("⏳ Waiting for proxy to initialize...")
        time.sleep(3)
        print("✅ Proxy should be ready!")
        
        logging.info("Initializing main window...")
        window = MainWindow(ca_cert)
        window.showMaximized()
        
        logging.info("Starting event loop...")
        sys.exit(app.exec())
        
    except Exception as e:
        logging.error(f"Failed to start: {str(e)}")
        QMessageBox.critical(None, "Error", f"Failed to start: {str(e)}")
        sys.exit(1)
    finally:
        if 'proxy_thread' in locals():
            logging.info("Shutting down mitmproxy thread...")
            proxy_thread.shutdown()
            proxy_thread.join()
            logging.info("mitmproxy thread shut down.")
