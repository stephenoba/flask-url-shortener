import os
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from hashids import Hashids

BASEDIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
db = SQLAlchemy()
app.config["SECRET_KEY"] = "AReallySecureSecretKeyShouldGoHere"
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + os.path.join(BASEDIR, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.app = app
db.init_app(app)
hashids = Hashids(min_length=4, salt=app.config['SECRET_KEY'])

class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    original_url = db.Column(db.String(800), nullable=False)
    clicks = db.Column(db.Integer, nullable=False, default=0)

with app.app_context():
    db.create_all()

@app.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'POST':
        url = request.form['url']

        if not url:
            flash('The URL is required!')
            return redirect(url_for('index'))

        url_data = URL(original_url=url)
        db.session.add(url_data)
        db.session.commit()

        hashid = hashids.encode(url_data.id)
        short_url = request.host_url + hashid

        return render_template('index.html', short_url=short_url)

    return render_template('index.html')


@app.route('/<id>')
def url_redirect(id):
    original_id = hashids.decode(id)
    if original_id:
        original_id = original_id[0]
        url_data = URL.query.filter_by(id=original_id).first_or_404()
        original_url = url_data.original_url

        url_data.clicks = url_data.clicks + 1
        db.session.add(url_data)
        db.session.commit()
        return redirect(original_url)
    else:
        flash('Invalid URL')
        return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)