import os
import src.utils.db as db
import src.blueprints.auth as auth
import src.blueprints.blog as blog
from flask import Flask


PORT = int(os.environ.get("PORT", 8080))
FLASK_SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")

app = Flask(__name__)
app.config["SECRET_KEY"] = FLASK_SECRET_KEY

db.init_app(app)
app.register_blueprint(auth.bp)
app.register_blueprint(blog.bp)
app.add_url_rule("/", endpoint="index")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=PORT)
