from library import app
from library import routes

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)