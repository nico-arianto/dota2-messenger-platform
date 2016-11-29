from flask import Flask

from route import initalize_routes

app = Flask(__name__)
initalize_routes(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
