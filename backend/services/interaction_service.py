from backend.extensions import db
from backend.models.drug_interaction import DrugInteraction


def normalize_name(name):
    """
    Convert medicine names into a standard format.
    Example:
    " Paracetamol " -> "paracetamol"
    """

    if not name:
        return ""

    return name.strip().lower()


def get_all_interactions():
    """
    Return all drug interactions.
    """

    return DrugInteraction.query.order_by(
        DrugInteraction.drug_one.asc()
    ).all()


def get_interaction_by_id(interaction_id):
    """
    Return one interaction using its ID.
    """

    return DrugInteraction.query.get_or_404(interaction_id)


def find_interaction(drug_one, drug_two):
    """
    Find interaction between two medicines.
    Search in both directions.
    """

    drug_one = normalize_name(drug_one)
    drug_two = normalize_name(drug_two)

    interaction = DrugInteraction.query.filter_by(
        drug_one=drug_one,
        drug_two=drug_two
    ).first()

    if interaction:
        return interaction

    interaction = DrugInteraction.query.filter_by(
        drug_one=drug_two,
        drug_two=drug_one
    ).first()

    return interaction


def add_interaction(data):
    """
    Add a new drug interaction.
    """

    existing = find_interaction(
        data.get("drug_one"),
        data.get("drug_two")
    )

    if existing:
        return existing

    interaction = DrugInteraction(

        drug_one=normalize_name(
            data.get("drug_one")
        ),

        drug_two=normalize_name(
            data.get("drug_two")
        ),

        severity=data.get("severity"),

        description=data.get("description"),

        recommendation=data.get("recommendation")

    )

    db.session.add(interaction)
    db.session.commit()

    return interaction


def update_interaction(interaction_id, data):
    """
    Update an existing interaction.
    """

    interaction = get_interaction_by_id(interaction_id)

    interaction.drug_one = normalize_name(
        data.get("drug_one")
    )

    interaction.drug_two = normalize_name(
        data.get("drug_two")
    )

    interaction.severity = data.get("severity")

    interaction.description = data.get("description")

    interaction.recommendation = data.get("recommendation")

    db.session.commit()

    return interaction


def delete_interaction(interaction_id):
    """
    Delete an interaction.
    """

    interaction = get_interaction_by_id(interaction_id)

    db.session.delete(interaction)

    db.session.commit()

    return True