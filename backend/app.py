from flask import Flask
from flask_cors import CORS
from routes.user_routes import user_routes  # 👈 route'ları import ediyoruz

app = Flask(__name__)
CORS(app)

ALLOWED_TEAMS = ['Galatasaray', 'Fenerbahçe', 'Beşiktaş', 'SAMSUNSPOR', 'trabzonspor']

# Blueprint kaydı
app.register_blueprint(user_routes)

if __name__ == "__main__":
    app.run(debug=True)
