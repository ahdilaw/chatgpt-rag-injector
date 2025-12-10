# main.py

import sys
import os
import time
from PySide6.QtWidgets import QApplication
from ui import MainWindow
from mitmproxy_integration import MitmProxyThread
import socket

if __name__ == "__main__":
    
    def find_free_port():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            return s.getsockname()[1]

    proxy_port = find_free_port()
    cdp_port = find_free_port()
    
    print(f"Starting proxy on port: {proxy_port}")
    print(f"Chrome DevTools on port: {cdp_port}")
    
    os.environ["QTWEBENGINE_REMOTE_DEBUGGING"] = str(cdp_port)
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = f"--proxy-server=127.0.0.1:{str(proxy_port)} --ignore-certificate-errors"

    app = QApplication(sys.argv)

    # Start the mitmproxy thread
    proxy_thread = MitmProxyThread(proxy_port)
    proxy_thread.start()

    # Wait for the proxy server to start
    print("Waiting for proxy to start...")
    time.sleep(5)
    print("Proxy should be ready!")

    window = MainWindow()
    window.showMaximized()

    app.exec()

    # Shutdown the mitmproxy thread
    proxy_thread.shutdown()
    proxy_thread.join()