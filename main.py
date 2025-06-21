from datetime import datetime
from flask import Flask, render_template, request, redirect
import os
from flask_sqlalchemy import SQLAlchemy
import re

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text, nullable=False)
    continent = db.Column(db.String(50), nullable=False)
    image = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, title, text, continent, image):
        self.title = title
        self.text = text
        self.continent = continent
        self.image = image

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)

    def __init__(self, login, password):
        self.login = login
        self.password = password


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        user = db.session.query(User).filter_by(login=login, password=password).first()
        if user:
            return redirect('/')
        else:
            return render_template('login.html', message='Невірний логін або пароль')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            return render_template('register.html', message='Паролі не співпадають')

        if not re.search(r'[A-Za-z]', password) or not re.search(r'\d', password):
            return render_template('register.html', message='Пароль має містити хоча б одну літеру і одну цифру')

        existing_user = db.session.query(User).filter_by(login=login).first()
        if existing_user:
            return render_template('register.html', message='Такий логін вже існує')

        new_user = User(login=login, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')

    return render_template('register.html')

@app.route('/articles')
def all_articles():
    articles = db.session.query(Article).all()
    return render_template('articles.html', articles=articles)

@app.route('/details/<int:id>')
def details(id):
    article = db.session.query(Article).get(id)
    return render_template('details.html', article=article)

@app.route('/add_article', methods=['GET', 'POST'])
def add_article():
    if request.method == 'POST':
        title = request.form['title']
        text = request.form['text']
        image = request.form['image']
        continent = request.form['continent']
        new_article = Article(title=title, text=text, continent=continent, image=image)
        db.session.add(new_article)
        db.session.commit()
        return redirect('/articles')
    return render_template('add_article.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)