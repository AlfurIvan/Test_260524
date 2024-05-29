import os
from flask_cors import CORS
from dotenv import load_dotenv, find_dotenv

from app import create_app

load_dotenv(find_dotenv())
app = create_app()
CORS(app)

if __name__ == '__main__':
    host = os.environ.get("SERVER_HOST")
    print(host)
    app.run(host=host)
