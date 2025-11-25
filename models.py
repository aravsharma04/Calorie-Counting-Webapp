from datetime import date
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from extensions import login_manager

@login_manager.user_loader
def load_user(user_id):
    from models import User  # avoid circular
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    age = db.Column(db.Integer, nullable=False)
    sex = db.Column(db.String(10), nullable=False)  # "male" / "female"
    height_cm = db.Column(db.Float, nullable=False)
    weight_kg = db.Column(db.Float, nullable=False)
    activity_level = db.Column(db.String(20), nullable=False)  # sedentary, light, etc.

    bmi = db.Column(db.Float)
    tdee = db.Column(db.Float)
    calorie_goal = db.Column(db.Float)  # current daily goal

    entries = db.relationship("Entry", backref="user", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def calculate_bmi(self):
        h_m = self.height_cm / 100.0
        return self.weight_kg / (h_m ** 2)

    def calculate_bmr(self):
        if self.sex.lower() == "male":
            return 10 * self.weight_kg + 6.25 * self.height_cm - 5 * self.age + 5
        else:
            return 10 * self.weight_kg + 6.25 * self.height_cm - 5 * self.age - 161

    def activity_multiplier(self):
        mapping = {
            "sedentary": 1.2,
            "light": 1.375,
            "moderate": 1.55,
            "heavy": 1.725,
            "athlete": 1.9,
        }
        return mapping.get(self.activity_level, 1.2)

    def calculate_tdee(self):
        return self.calculate_bmr() * self.activity_multiplier()

    def update_metrics(self):
        self.bmi = self.calculate_bmi()
        self.tdee = self.calculate_tdee()
        # default calorie goal as mild deficit
        if not self.calorie_goal:
            self.calorie_goal = self.tdee - 300


class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(10), nullable=False)  # "food" or "exercise"
    name = db.Column(db.String(80), nullable=False)
    calories = db.Column(db.Integer, nullable=False)
    day = db.Column(db.Date, default=date.today, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
