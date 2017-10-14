import logging

from tech_forum_api.app import app

logging.basicConfig(level=logging.INFO)
logging.exception("HERE HELLO MAIN.PY")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
