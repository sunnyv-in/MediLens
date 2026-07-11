from datetime import datetime

def is_reminder_due(reminder_time):
    """
    Returns True if reminder should trigger this minute.
    reminder_time should be a datetime.time object.
    """

    now = datetime.now().time()

    return (
        now.hour == reminder_time.hour and
        now.minute == reminder_time.minute
    )


def reminder_status(reminder):
    """
    Returns reminder state.
    """

    if not reminder.is_active:
        return "Inactive"

    if is_reminder_due(reminder.reminder_time):
        return "Due"

    return "Scheduled"