import calendar
from datetime import date
from datetime import datetime

def parse_medicine_date(date_string):
    if not date_string:
        return None

    cleaned_date = date_string.strip().upper()

    date_formats = [
        "%b.%y",   # JAN.26
        "%b %y",   # JAN 26
        "%b.%Y",   # JAN.2026
        "%b %Y",   # JAN 2026
        "%m/%y",   # 01/26
        "%m/%Y",   # 01/2026
        "%m-%y",   # 01-26
        "%m-%Y",   # 01-2026
    ]

    for date_format in date_formats:
        try:
            return datetime.strptime(cleaned_date, date_format)
        except ValueError:
            continue

    return None

def get_expiry_date(date_string):
    parsed = parse_medicine_date(date_string)
    if parsed is None:
        return None

    last_day = calendar.monthrange(parsed.year, parsed.month)[1]
    return parsed.replace(day=last_day).date()

def get_expiry_status(expiry_date):
    if expiry_date is None:
        return "Unknown"

    today = date.today()
    days_left = (expiry_date - today).days

    if days_left < 0:
        return "Expired"
    elif days_left <= 30:
        return "Expiring soon"
    else:
        return "Safe"


#use below for testing
if __name__ == "__main__":
    test_dates = ["JUL.26", "DEC.27", "05/2027", "", "GARBAGE"]
    for d in test_dates:
        exp = get_expiry_date(d)
        status = get_expiry_status(exp)
        print(f"{d!r:15} -> {exp} -> {status}")