from uuid import uuid4

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
)

from flask_login import (
    login_user,
    logout_user,
    current_user,
    login_required,
)

from backend.extensions import db

from backend.models.user import User
from backend.models.medicine import Medicine
from backend.models.medicine_history import MedicineHistory
from backend.models.reminder import MedicationReminder

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


# ============================================================
# MIGRATE GUEST DATA TO USER ACCOUNT
# ============================================================


@auth_bp.route("/migrate-guest")
@login_required
def migrate_guest():

    guest_id = session.get("guest_id")

    if not guest_id:
        return redirect(url_for("home.home"))

    try:
        # Migrate medicines
        medicines = Medicine.query.filter_by(guest_id=guest_id).all()

        for medicine in medicines:
            medicine.user_id = current_user.id
            medicine.guest_id = None

        # Migrate medicine history
        history = MedicineHistory.query.filter_by(guest_id=guest_id).all()

        for item in history:
            item.user_id = current_user.id
            item.guest_id = None

        # Migrate reminders
        reminders = MedicationReminder.query.filter_by(guest_id=guest_id).all()

        for reminder in reminders:
            reminder.user_id = current_user.id
            reminder.guest_id = None

        db.session.commit()

        session.pop("guest_id", None)

        flash(
            "Your guest data has been added to your account.",
            "success",
        )

    except Exception:
        db.session.rollback()

        flash(
            "Could not migrate guest data.",
            "error",
        )

    return redirect(url_for("home.home"))


# ============================================================
# REGISTER
# ============================================================


@auth_bp.route("/register", methods=["GET", "POST"])
def register():

    if current_user.is_authenticated:
        return redirect(url_for("home.home"))

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        # Validate fields
        if not name or not email or not password:
            flash("Please fill all fields.", "error")
            return render_template("auth/register.html")

        # Validate password
        if len(password) < 8:
            flash(
                "Password must be at least 8 characters.",
                "error",
            )
            return render_template("auth/register.html")

        # Check existing user
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("Email already registered.", "error")
            return render_template("auth/register.html")

        # Create user
        try:
            user = User(name=name, email=email)

            user.set_password(password)

            db.session.add(user)
            db.session.commit()

            login_user(user)

            flash(
                "Account created successfully.",
                "success",
            )

            return redirect(url_for("auth.migrate_guest"))

        except Exception:
            db.session.rollback()

            flash(
                "Could not create your account. Please try again.",
                "error",
            )

            return render_template("auth/register.html")

    return render_template("auth/register.html")


# ============================================================
# UPDATE PHONE NUMBER
# ============================================================


@auth_bp.route("/account/phone", methods=["POST"])
@login_required
def update_phone():

    phone = request.form.get("phone_number", "").strip()

    # Validate phone number
    if phone:
        cleaned_phone = phone.replace("+", "").replace(" ", "").replace("-", "")

        if not cleaned_phone.isdigit():
            flash("Enter a valid phone number.", "error")
            return redirect(url_for("auth.account"))

    try:
        current_user.phone_number = phone or None

        db.session.commit()

        flash(
            "Emergency contact number saved.",
            "success",
        )

    except Exception:
        db.session.rollback()

        flash(
            "Could not save your phone number.",
            "error",
        )

    return redirect(url_for("auth.account"))


# ============================================================
# LOGIN
# ============================================================


@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("home.home"))

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        # Validate fields
        if not email or not password:
            flash(
                "Please enter your email and password.",
                "error",
            )
            return render_template("auth/login.html")

        # Find user
        user = User.query.filter_by(email=email).first()

        # Check password
        if user is None or not user.check_password(password):
            flash(
                "Invalid email or password.",
                "error",
            )
            return render_template("auth/login.html")

        # Login
        login_user(user)

        flash("Welcome back!", "success")

        return redirect(url_for("auth.migrate_guest"))

    return render_template("auth/login.html")


# ============================================================
# CONTINUE AS GUEST
# ============================================================


@auth_bp.route("/guest")
def guest():

    if "guest_id" not in session:
        session["guest_id"] = str(uuid4())

    session.permanent = True

    return redirect(url_for("scan.scan"))


# ============================================================
# MY ACCOUNT
# ============================================================


@auth_bp.route("/account")
@login_required
def account():

    return render_template(
        "auth/account.html",
        user=current_user,
    )


# ============================================================
# FORGOT PASSWORD
# ============================================================


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()

        if not email:
            flash(
                "Please enter your email address.",
                "error",
            )
            return render_template("auth/forgot_password.html")

        # Check account
        user = User.query.filter_by(email=email).first()

        # Email reset functionality can be added later.
        # Use the same message whether the account exists or not.

        flash(
            "If an account exists with this email, "
            "password recovery instructions will be provided.",
            "success",
        )

        return redirect(url_for("auth.forgot_password"))

    return render_template("auth/forgot_password.html")


# ============================================================
# CHANGE PASSWORD
# ============================================================


@auth_bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():

    if request.method == "POST":

        current_password = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Validate current password
        if not current_user.check_password(current_password):
            flash(
                "Current password is incorrect.",
                "error",
            )
            return render_template("auth/change_password.html")

        # Validate new password
        if len(new_password) < 8:
            flash(
                "New password must be at least 8 characters.",
                "error",
            )
            return render_template("auth/change_password.html")

        # Confirm password
        if new_password != confirm_password:
            flash(
                "New passwords do not match.",
                "error",
            )
            return render_template("auth/change_password.html")

        # Prevent same password
        if current_password == new_password:
            flash(
                "New password must be different from your current password.",
                "error",
            )
            return render_template("auth/change_password.html")

        # Change password
        try:
            current_user.set_password(new_password)

            db.session.commit()

            flash(
                "Password changed successfully.",
                "success",
            )

            return redirect(url_for("auth.account"))

        except Exception:
            db.session.rollback()

            flash(
                "Could not change your password. Please try again.",
                "error",
            )

            return render_template("auth/change_password.html")

    return render_template("auth/change_password.html")


# ============================================================
# LOGOUT
# ============================================================


@auth_bp.route("/logout")
@login_required
def logout():

    logout_user()

    flash(
        "You have been logged out.",
        "success",
    )

    return redirect(url_for("home.home"))
