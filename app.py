from flask import Flask, redirect, url_for, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SECRET_KEY"] = "littlemovie6988"


db = SQLAlchemy()

login_manager = LoginManager()
login_manager.init_app(app)

class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True,
                         nullable=False)
    password_h = db.Column(db.String(250),
                         nullable=False)
    email = db.Column(db.String(250),
                         nullable=False)
    
    def set_password(self, password):
        self.password_h = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_h, password)


db.init_app(app)


@login_manager.user_loader
def loader_user(user_id):
    return Users.query.get(int(user_id))


with app.app_context():
    db.create_all()

@app.route("/")
def vi():
    return redirect(url_for("home"))

@app.route('/home')
def home():
    return render_template("home.html")


@app.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == "POST":
        user = Users.query.filter_by(email=request.form.get("email")).first()
        if not user is None:
            if user.check_password(request.form.get("password")):
                login_user(user)
                return redirect(url_for("home"))
            return render_template("er_wrong_password.html")
        return render_template("er_log_email.html")
    return render_template("login.html")

@app.route('/sing_up', methods=["GET", "POST"])
def sing_up():
    if request.method == "POST":
        if request.form.get("password") == request.form.get("try_password"):
            if db.session.query(Users).filter_by(email=request.form.get("email")).count() < 1:
                if db.session.query(Users).filter_by(username=request.form.get("username")).count() < 1:
                    user = Users(username=request.form.get("username"),  
                                    email=request.form.get("email"))
                    user.set_password(request.form.get("password"))
                    db.session.add(user)
                    db.session.commit()
                    return redirect(url_for("login"))
                else: return render_template("er_username.html")
            else: return render_template("er_email.html")
        else: return render_template("er_try_pass.html")
    return render_template("sing_up.html")



@app.route('/logout', methods=["GET", "POST"])
@login_required
def logout():
    if request.method == "POST":
        logout_user()
        return redirect(url_for('home'))
    return render_template("logout.html")

@app.route('/profile', methods=["GET", "POST"])
@login_required
def profile():
    return render_template("profile.html")


@app.route('/profile/change_password/', methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        if request.form.get("password") == request.form.get("try_password"):
            if not (current_user.check_password(request.form.get("password"))):
                user = current_user
                db.session.delete(user)
                user.set_password(request.form.get("password")) 
                db.session.add(user)
                db.session.commit()
                login_user(user)
                return redirect(url_for('home'))
            else: return render_template("er_try_new_password.html")
        else: return render_template("er_try_pass2.html")
    return render_template("change_password.html")


if __name__ == '__main__':
    app.run(debug=True)