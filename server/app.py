
#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, session
from flask_migrate import Migrate

from models import db, Article, User, ArticleSchema, UserSchema

app = Flask(__name__)

app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


# Clear the session
@app.route('/clear')
def clear_session():
    session['page_views'] = 0
    return {'message': '200: Successfully cleared session data.'}, 200


# Get all articles
@app.route('/articles')
def index_articles():
    articles = [ArticleSchema().dump(a) for a in Article.query.all()]
    return make_response(articles)


# Get one article and enforce the paywall
@app.route('/articles/<int:id>')
def show_article(id):

    # Step 1: Initialize page_views if this is the first request
    if 'page_views' not in session:
        session['page_views'] = 0

    # Step 2: Increment page_views on every request
    session['page_views'] += 1

    # Step 3: Check whether the user has exceeded the limit
    if session['page_views'] > 3:
        return jsonify({
            'message': 'Maximum pageview limit reached'
        }), 401

    # Find the requested article
    article = Article.query.filter_by(id=id).first()

    if article is None:
        return jsonify({
            'message': 'Article not found'
        }), 404

    # Convert the article into JSON data
    article_data = ArticleSchema().dump(article)

    return jsonify(article_data), 200


if __name__ == '__main__':
    app.run(port=5555)
