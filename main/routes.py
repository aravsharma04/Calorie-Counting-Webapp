from datetime import date, timedelta
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from . import main
from extensions import db
from models import Entry
from ml.goal_model import recommend_goal


@main.route("/")
@login_required
def index():
    today = date.today()
    entries = (
        Entry.query
        .filter_by(user_id=current_user.id, day=today)
        .order_by(Entry.id.desc())
        .all()
    )

    total_food = sum(e.calories for e in entries if e.type == "food")
    total_exercise = sum(e.calories for e in entries if e.type == "exercise")
    net = total_food - total_exercise

    # last 7 days for mini chart / ML
    days = []
    net_values = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        ds = Entry.query.filter_by(user_id=current_user.id, day=d).all()
        tf = sum(e.calories for e in ds if e.type == "food")
        te = sum(e.calories for e in ds if e.type == "exercise")
        days.append(d.strftime("%a"))
        net_values.append(tf - te)

    avg_net_7d = sum(net_values) / len(net_values) if net_values else current_user.tdee

    return render_template(
        "index.html",
        entries=entries,
        total_food=total_food,
        total_exercise=total_exercise,
        net=net,
        calorie_goal=current_user.calorie_goal,
        days=days,
        net_values=net_values,
    )


@main.route("/add", methods=["POST"])
@login_required
def add_entry():
    entry_type = request.form.get("type")  # "food" or "exercise"
    name = request.form.get("name")
    calories = int(request.form.get("calories"))

    entry = Entry(
        type=entry_type,
        name=name,
        calories=calories,
        user_id=current_user.id,
    )
    db.session.add(entry)
    db.session.commit()
    flash("Entry added.")
    return redirect(url_for("main.index"))


@main.route("/delete/<int:id>")
@login_required
def delete_entry(id):
    entry = Entry.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(entry)
    db.session.commit()
    flash("Entry deleted.")
    return redirect(url_for("main.index"))


@main.route("/profile")
@login_required
def profile():
    # recalc in case weight changed later (you could add an edit form too)
    current_user.update_metrics()
    db.session.commit()
    return render_template("profile.html", user=current_user)


@main.route("/recalculate_goal")
@login_required
def recalculate_goal():
    today = date.today()

    # last 7 days average net cals
    net_values = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        ds = Entry.query.filter_by(user_id=current_user.id, day=d).all()
        tf = sum(e.calories for e in ds if e.type == "food")
        te = sum(e.calories for e in ds if e.type == "exercise")
        net_values.append(tf - te)

    avg_net_7d = sum(net_values) / len(net_values) if net_values else current_user.tdee

    new_goal = recommend_goal(
        tdee=current_user.tdee,
        avg_net_7d=avg_net_7d,
        current_goal=current_user.calorie_goal,
    )

    current_user.calorie_goal = new_goal
    db.session.commit()
    flash(f"New recommended daily goal: {int(new_goal)} kcal")
    return redirect(url_for("main.profile"))
