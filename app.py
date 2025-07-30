from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = "secret"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bugs.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    email = db.Column(db.String(120))

class Bug(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.String(300))
    priority = db.Column(db.String(10))
    status = db.Column(db.String(10), default="Open")
    assigned_to = db.Column(db.String(80))

with app.app_context():
    db.create_all()

def send_email(to_email, subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = "noreply@example.com"
    msg["To"] = to_email
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login("youremail@gmail.com", "yourpassword")
        server.sendmail("youremail@gmail.com", to_email, msg.as_string())
        server.quit()
    except:
        pass

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()
        if user:
            session["user"] = user.username
            return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    users = User.query.all()
    bugs = Bug.query.all()
    if request.method == "POST":
        title = request.form["title"]
        desc = request.form["description"]
        priority = request.form["priority"]
        assigned = request.form["assigned"]
        bug = Bug(title=title, description=desc, priority=priority, assigned_to=assigned)
        db.session.add(bug)
        db.session.commit()
        assigned_user = User.query.filter_by(username=assigned).first()
        if assigned_user:
            send_email(assigned_user.email, "New Bug Assigned", f"{title}\n{desc}")

    return render_template("dashboard.html", users=users, bugs=bugs)

@app.route("/update/<int:id>")
def update(id):
    if "user" not in session:
        return redirect(url_for("login"))
    bug = Bug.query.get(id)
    bug.status = "Fixed"
    db.session.commit()
    return redirect(url_for("dashboard"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)