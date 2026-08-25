from uuid import uuid4

from flask import session
from flask_login import current_user


def get_guest_id():

    if "guest_id" not in session:

        session["guest_id"] = str(uuid4())

    session.permanent = True

    return session["guest_id"]


def get_owner_values():

    if current_user.is_authenticated:

        return {"user_id": current_user.id, "guest_id": None}

    return {"user_id": None, "guest_id": get_guest_id()}
