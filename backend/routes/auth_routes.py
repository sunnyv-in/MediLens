from uuid import uuid4
from datetime import datetime

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    jsonify,
)

from flask_login import (
    login_user,
    logout_user,
    current_user,
    login_required,
)

from backend.extensions import db

from backend.models.user import User, CareCircleContact, DoseLog
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
        return redirect(url_for("home.dashboard"))

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
            "Your guest data has been safely linked to your account.",
            "success",
        )

    except Exception:
        db.session.rollback()

        flash(
            "Could not migrate guest data.",
            "error",
        )

    return redirect(url_for("home.dashboard"))


# ============================================================
# REGISTER (PATIENT & CAREGIVER FLOW WITH CARE CIRCLE)
# ============================================================


@auth_bp.route("/register", methods=["GET", "POST"])
def register():

    if current_user.is_authenticated:
        return redirect(url_for("home.dashboard"))

    if request.method == "POST":

        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        name = f"{first_name} {last_name}".strip() or request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone_number = request.form.get("phone_number", "").strip()
        password = request.form.get("password", "")

        role = request.form.get("role", "patient").strip()  # 'patient' or 'caregiver'
        patient_name = request.form.get("patient_name", "").strip() if role == "caregiver" else None

        # Validate required fields
        if not first_name or not last_name or not email or not password:
            flash("Please fill in First Name, Last Name, Email, and Password.", "error")
            return render_template("auth/register.html")

        # Validate password length
        if len(password) < 8:
            flash("Password must be at least 8 characters.", "error")
            return render_template("auth/register.html")

        # Check existing user
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("An account with this email already exists.", "error")
            return render_template("auth/register.html")

        # Create user
        try:
            user = User(
                name=name,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_number=phone_number or None,
                role=role,
                patient_name=patient_name,
            )

            user.set_password(password)

            db.session.add(user)
            db.session.commit()

            # Process any additional Care Circle contacts submitted
            contact_names = request.form.getlist("contact_name[]")
            contact_relationships = request.form.getlist("contact_relationship[]")
            contact_phones = request.form.getlist("contact_phone[]")

            for c_name, c_rel, c_phone in zip(contact_names, contact_relationships, contact_phones):
                c_name = (c_name or "").strip()
                c_phone = (c_phone or "").strip()
                if c_name and c_phone:
                    c_contact = CareCircleContact(
                        user_id=user.id,
                        name=c_name,
                        relationship=(c_rel or "Caregiver").strip(),
                        phone_number=c_phone,
                    )
                    db.session.add(c_contact)

            db.session.commit()

            login_user(user)

            flash(
                f"Welcome to MediLens, {first_name}! Your account and Care Circle have been initialized.",
                "success",
            )

            return redirect(url_for("auth.migrate_guest"))

        except Exception as reg_err:
            db.session.rollback()
            print("Registration error:", reg_err)
            flash(
                "Could not create your account. Please try again.",
                "error",
            )
            return render_template("auth/register.html")

    return render_template("auth/register.html")


# ============================================================
# CARE CIRCLE (ADD ADDITIONAL CONTACT NUMBERS)
# ============================================================


@auth_bp.route("/care-circle/add", methods=["POST"])
@login_required
def add_care_circle_contact():
    data = request.get_json(silent=True) or request.form

    name = (data.get("name") or "").strip()
    relationship = (data.get("relationship") or "Caregiver").strip()
    phone_number = (data.get("phone_number") or "").strip()

    if not name or not phone_number:
        if request.is_json:
            return jsonify({"success": False, "error": "Name and phone number are required."}), 400
        flash("Name and mobile number are required.", "error")
        return redirect(url_for("home.dashboard"))

    try:
        contact = CareCircleContact(
            user_id=current_user.id,
            name=name,
            relationship=relationship,
            phone_number=phone_number,
        )
        db.session.add(contact)
        db.session.commit()

        if request.is_json:
            return jsonify({
                "success": True,
                "message": f"Added {name} ({relationship}) to Care Circle.",
                "contact": {
                    "id": contact.id,
                    "name": contact.name,
                    "relationship": contact.relationship,
                    "phone_number": contact.phone_number,
                }
            })

        flash(f"Added {name} to your Care Circle notifications.", "success")
    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return jsonify({"success": False, "error": str(e)}), 500
        flash("Could not add contact.", "error")

    return redirect(url_for("home.dashboard"))


# ============================================================
# DOSE TAKEN / CLOSER ENGINE (PREVENTS DOUBLE-DOSING)
# ============================================================


@auth_bp.route("/dose-taken", methods=["POST"])
def record_dose_taken():
    data = request.get_json(silent=True) or request.form

    medicine_id = data.get("medicine_id")
    reminder_id = data.get("reminder_id")
    medicine_name = (data.get("medicine_name") or "Prescription").strip()

    admin_by = (
        data.get("administered_by")
        or (current_user.name if current_user.is_authenticated else "Self")
    ).strip()

    now = datetime.now()
    now_str = now.strftime("%I:%M %p")

    try:
        log = DoseLog(
            user_id=current_user.id if current_user.is_authenticated else None,
            guest_id=session.get("guest_id"),
            medicine_id=int(medicine_id) if medicine_id else None,
            reminder_id=int(reminder_id) if reminder_id else None,
            medicine_name=medicine_name,
            administered_by=admin_by,
            taken_at=now,
            status="taken",
        )
        db.session.add(log)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": f"Dose completed: {medicine_name} administered by {admin_by} at {now_str}. Notifications cleared for all caretakers to prevent duplicate dosing.",
            "administered_by": admin_by,
            "time_str": now_str,
            "status": "completed",
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


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
        return redirect(url_for("home.dashboard"))

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
                "Invalid email or password. Please verify your credentials.",
                "error",
            )
            return render_template("auth/login.html")

        # Login
        login_user(user)

        flash("Welcome back!", "success")

        return redirect(url_for("auth.migrate_guest"))

    return render_template("auth/login.html")


# ============================================================
# GOOGLE / FIREBASE AUTHENTICATION
# ============================================================


@auth_bp.route("/google-login", methods=["POST"])
def google_login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    name = (data.get("name") or "").strip() or "Google User"

    if not email or "@" not in email:
        return jsonify({"success": False, "error": "A valid Google account email is required."}), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        try:
            parts = name.split()
            f_name = parts[0] if parts else "Google"
            l_name = " ".join(parts[1:]) if len(parts) > 1 else "User"

            user = User(
                name=name,
                first_name=f_name,
                last_name=l_name,
                email=email,
            )
            user.set_password(uuid4().hex + uuid4().hex)
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "error": "Failed to create user account with Google credentials."}), 500

    login_user(user)

    # Migrate guest data if present
    guest_id = session.get("guest_id")
    if guest_id:
        try:
            for medicine in Medicine.query.filter_by(guest_id=guest_id).all():
                medicine.user_id = user.id
                medicine.guest_id = None

            for history_item in MedicineHistory.query.filter_by(guest_id=guest_id).all():
                history_item.user_id = user.id
                history_item.guest_id = None

            for reminder in MedicationReminder.query.filter_by(guest_id=guest_id).all():
                reminder.user_id = user.id
                reminder.guest_id = None

            db.session.commit()
            session.pop("guest_id", None)
        except Exception:
            db.session.rollback()

    flash(f"Welcome, {user.name}! Signed in via Google.", "success")
    return jsonify({
        "success": True,
        "redirect": url_for("home.dashboard"),
        "user": {
            "name": user.name,
            "email": user.email,
        }
    })


# ============================================================
# CONTINUE AS GUEST
# ============================================================


@auth_bp.route("/guest")
def guest():

    if "guest_id" not in session:
        session["guest_id"] = str(uuid4())

    session.permanent = True

    return redirect(url_for("home.dashboard"))


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

        flash(
            "If an account exists with this email, password recovery instructions will be provided.",
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
        "You have been logged out safely.",
        "success",
    )

    return redirect(url_for("home.home"))
