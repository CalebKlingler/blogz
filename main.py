from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text())
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password


@app.route('/blog', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        if title =='' or body =='':
            return render_template('newpost.html', error = "Please enter both a title and a body for your new blog.")
        new_blog = Blog(title,body)
        db.session.add(new_blog)
        db.session.commit()
    
    if request.args.get('id'):
        blog_id = request.args.get('id')
        
        blogs = Blog.query.filter_by(id=blog_id).all()
        return render_template('single_blog.html', blogs=blogs)
    else:
        blogs = Blog.query.all()
        return render_template('build-a-blog.html', title="Build a Blog", blogs=blogs)

@app.route('/newpost', methods=["GET", "POST"])
def newpost():
    

    return render_template('newpost.html', title="Add Blog Entry")


if __name__ == "__main__":

    app.run()
