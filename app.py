from flask import Flask

from middleware import initialize_data_access
from route import initalize_routes

app = Flask(__name__)
initialize_data_access(app=app)
initalize_routes(app=app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
