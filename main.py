from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

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
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'blog']
    if request.endpoint not in allowed_routes and'username' not in session:
        return redirect('/login')



@app.route('/blog', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        owner = User.query.filter_by(username=session['username']).first()
        if title =='' or body =='':
            return render_template('newpost.html', error = "Please enter both a title and a body for your new blog.")
        new_blog = Blog(title, body, owner)
        db.session.add(new_blog)
        db.session.commit()
    
    if request.args.get('id'):
        blog_id = request.args.get('id')
        
        blogs = Blog.query.filter_by(id=blog_id).all()
        return render_template('single_blog.html', blogs=blogs)
    else:
        blogs = Blog.query.all()
        return render_template('build-a-blog.html', title="Blogz", blogs=blogs)

@app.route('/newpost', methods=["GET", "POST"])
def newpost():
    

    return render_template('newpost.html', title="Add Blog Entry")


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            print(session)
            return redirect('/newpost')
        elif not user:
            flash("User does not exist.", 'error')
        else:
            flash("Password is incorrect.", 'error')
    return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    def is_valid(word):
        if word == '' or len(word) < 3 or len(word) > 20:
            return False
        else:
            for char in word:
                if char == ' ':
                    return False
            return True
    def are_matching(password,verpassword):
        if verpassword == '':
            return False
        if password == verpassword:
            return True
        else:
            return False

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        user_error=''
        pass_error=''
        verpass_error=''
        email_error=''
        verpass_valid=''
        if not is_valid(username):
            user_error = 'y'
    
        if not is_valid(password):
            pass_error = 'y'
        
        if not are_matching(password,verify):
            verpass_error = 'y'

        if not is_valid(verify):
            verpass_valid = 'y'
            verpass_error = ''
        if not is_valid(username) or not is_valid(password) or not is_valid(verify) or not are_matching(password, verify):
            return render_template('register.html', verpassvalid = verpass_valid, verpassworderror=verpass_error, passerror=pass_error,  usererror=user_error, username=username)

        #TODO - validate
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            #TODO user better response messaging
            flash("Duplicate User.", 'error')

    return render_template('register.html')


@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

if __name__ == "__main__":

    app.run()
