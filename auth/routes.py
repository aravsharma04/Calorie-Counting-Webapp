from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from extensions import db
from models import User


@auth.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        age = int(request.form.get("age"))
        sex = request.form.get("sex")
        height_cm = float(request.form.get("height_cm"))
        weight_kg = float(request.form.get("weight_kg"))
        activity_level = request.form.get("activity_level")

        if User.query.filter_by(username=username).first():
            flash("Username already exists.")
            return redirect(url_for("auth.register"))

        user = User(
            username=username,
            age=age,
            sex=sex,
            height_cm=height_cm,
            weight_kg=weight_kg,
            activity_level=activity_level,
        )
        user.set_password(password)
        user.update_metrics()

        db.session.add(user)
        db.session.commit()
        flash("Registered successfully. Please log in.")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash("Logged in successfully.")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.index"))
        else:
            flash("Invalid username or password.")

    return render_template("auth/login.html")


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.")
    return redirect(url_for("auth.login"))
