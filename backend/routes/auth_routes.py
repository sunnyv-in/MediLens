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
def migrate_guest():

    # User must be logged in
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))

    # Get guest session ID
    guest_id = session.get("guest_id")

    # Nothing to migrate
    if not guest_id:
        return redirect(url_for("home.home"))

    try:

        # ----------------------------------------------------
        # Migrate medicines
        # ----------------------------------------------------

        medicines = Medicine.query.filter_by(guest_id=guest_id).all()

        for medicine in medicines:
            medicine.user_id = current_user.id
            medicine.guest_id = None

        # ----------------------------------------------------
        # Migrate medicine history
        # ----------------------------------------------------

        history = MedicineHistory.query.filter_by(guest_id=guest_id).all()

        for item in history:
            item.user_id = current_user.id
            item.guest_id = None

        # ----------------------------------------------------
        # Migrate reminders
        # ----------------------------------------------------

        reminders = MedicationReminder.query.filter_by(guest_id=guest_id).all()

        for reminder in reminders:
            reminder.user_id = current_user.id
            reminder.guest_id = None

        # Save everything
        db.session.commit()

        # Remove guest ID after successful migration
        session.pop("guest_id", None)

        flash("Your guest data has been added to your account.", "success")

    except Exception:

        db.session.rollback()

        flash("Could not migrate guest data.", "error")

    return redirect(url_for("home.home"))


# ============================================================
# REGISTER
# ============================================================


@auth_bp.route("/register", methods=["GET", "POST"])
def register():

    # Already logged in
    if current_user.is_authenticated:
        return redirect(url_for("home.home"))

    if request.method == "POST":

        # Get form values
        name = request.form.get("name", "").strip()

        email = request.form.get("email", "").strip().lower()

        password = request.form.get("password", "")

        # ----------------------------------------------------
        # Basic validation
        # ----------------------------------------------------

        if not name or not email or not password:

            flash("Please fill all fields.", "error")

            return render_template("auth/register.html")

        # ----------------------------------------------------
        # Password validation
        # ----------------------------------------------------

        if len(password) < 8:

            flash("Password must be at least 8 characters.", "error")

            return render_template("auth/register.html")

        # ----------------------------------------------------
        # Check existing user
        # ----------------------------------------------------

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:

            flash("Email already registered.", "error")

            return render_template("auth/register.html")

        # ----------------------------------------------------
        # Create user
        # ----------------------------------------------------

        try:

            user = User(name=name, email=email)

            # Hash password
            user.set_password(password)

            db.session.add(user)
            db.session.commit()

            # Automatically log user in
            login_user(user)

            flash("Account created successfully.", "success")

            # Migrate guest data if available
            return redirect(url_for("auth.migrate_guest"))

        except Exception:

            db.session.rollback()

            flash("Could not create your account. Please try again.", "error")

            return render_template("auth/register.html")

    return render_template("auth/register.html")


# ============================================================
# LOGIN
# ============================================================


@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    # Already logged in
    if current_user.is_authenticated:
        return redirect(url_for("home.home"))

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()

        password = request.form.get("password", "")

        # ----------------------------------------------------
        # Validate fields
        # ----------------------------------------------------

        if not email or not password:

            flash("Please enter your email and password.", "error")

            return render_template("auth/login.html")

        # ----------------------------------------------------
        # Find user
        # ----------------------------------------------------

        user = User.query.filter_by(email=email).first()

        # ----------------------------------------------------
        # Check password
        # ----------------------------------------------------

        if user is None or not user.check_password(password):

            flash("Invalid email or password.", "error")

            return render_template("auth/login.html")

        # ----------------------------------------------------
        # Login
        # ----------------------------------------------------

        login_user(user)

        flash("Welcome back!", "success")

        # Migrate guest data if present
        return redirect(url_for("auth.migrate_guest"))

    return render_template("auth/login.html")


# ============================================================
# CONTINUE AS GUEST
# ============================================================


@auth_bp.route("/guest")
def guest():

    # Create guest ID if one does not exist
    if "guest_id" not in session:

        session["guest_id"] = str(uuid4())

    # Keep guest session
    session.permanent = True

    return redirect(url_for("scan.scan"))


# ============================================================
# MY ACCOUNT
# ============================================================


@auth_bp.route("/account")
def account():

    # Login required
    if not current_user.is_authenticated:

        return redirect(url_for("auth.login"))

    return render_template("auth/account.html", user=current_user)


# ============================================================
# FORGOT PASSWORD
# ============================================================


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()

        # ----------------------------------------------------
        # Validate email
        # ----------------------------------------------------

        if not email:

            flash("Please enter your email address.", "error")

            return render_template("auth/forgot_password.html")

        # ----------------------------------------------------
        # Check account
        # ----------------------------------------------------

        user = User.query.filter_by(email=email).first()

        # ----------------------------------------------------
        # Current hackathon implementation
        # ----------------------------------------------------
        #
        # We deliberately show the same message whether the
        # account exists or not.
        #
        # Actual email reset can be added later.
        # ----------------------------------------------------

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
def change_password():

    # Login required
    if not current_user.is_authenticated:

        return redirect(url_for("auth.login"))

    if request.method == "POST":

        current_password = request.form.get("current_password", "")

        new_password = request.form.get("new_password", "")

        confirm_password = request.form.get("confirm_password", "")

        # ----------------------------------------------------
        # Validate current password
        # ----------------------------------------------------

        if not current_user.check_password(current_password):

            flash("Current password is incorrect.", "error")

            return render_template("auth/change_password.html")

        # ----------------------------------------------------
        # Validate new password
        # ----------------------------------------------------

        if len(new_password) < 8:

            flash("New password must be at least 8 characters.", "error")

            return render_template("auth/change_password.html")

        # ----------------------------------------------------
        # Confirm password
        # ----------------------------------------------------

        if new_password != confirm_password:

            flash("New passwords do not match.", "error")

            return render_template("auth/change_password.html")

        # ----------------------------------------------------
        # Prevent same password
        # ----------------------------------------------------

        if current_password == new_password:

            flash("New password must be different from your current password.", "error")

            return render_template("auth/change_password.html")

        # ----------------------------------------------------
        # Change password
        # ----------------------------------------------------

        try:

            current_user.set_password(new_password)

            db.session.commit()

            flash("Password changed successfully.", "success")

            return redirect(url_for("auth.account"))

        except Exception:

            db.session.rollback()

            flash("Could not change your password. Please try again.", "error")

            return render_template("auth/change_password.html")

    return render_template("auth/change_password.html")


# ============================================================
# LOGOUT
# ============================================================


@auth_bp.route("/logout")
def logout():

    logout_user()

    flash("You have been logged out.", "success")

    return redirect(url_for("home.home"))
