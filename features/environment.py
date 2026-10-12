"""Run BDD against a real local HTTP server and headless Chrome."""
import os
import threading
from werkzeug.serving import make_server
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

def before_all(context):
    os.environ["DATABASE_URI"] = "sqlite:///:memory:"
    from service import app
    context.app = app
    context.server = make_server("127.0.0.1", 0, app, threaded=True)
    context.base_url = f"http://127.0.0.1:{context.server.server_port}"
    context.server_thread = threading.Thread(target=context.server.serve_forever, daemon=True)
    context.server_thread.start()
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    if os.getenv("CHROME_BINARY"):
        options.binary_location = os.environ["CHROME_BINARY"]
    service = Service(executable_path=os.environ["CHROMEDRIVER"]) if os.getenv("CHROMEDRIVER") else Service()
    context.driver = webdriver.Chrome(service=service, options=options)
    context.wait_seconds = 10

def after_all(context):
    if hasattr(context, "driver"):
        context.driver.quit()
    if hasattr(context, "server"):
        context.server.shutdown()
        context.server_thread.join(timeout=5)
