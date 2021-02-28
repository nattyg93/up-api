#!/usr/bin/env python3
"""Get and return groceries balance."""
from datetime import date, datetime, time
from decimal import Decimal

from dateutil import relativedelta

from api import Account, up_auth

MONDAY = 1
SUNDAY = 0
MIDNIGHT = time.min
SIX_AM = time(6)

user_config = {
    "nat": {
        "API_TOKEN_ENV_VARIABLE": "UP_API_TOKEN_NAT",
        "ACCOUNT_NAME": "Groceries",
        "WEEKS_PER_WAGE_CYCLE": 2,
        "WAGE_CYCLE_START": date(2021, 2, 22),
        "DEPOSITED": (MONDAY, SIX_AM),
        "WEEKLY_BUDGET": Decimal(62.50),
    },
    "kait": {
        "API_TOKEN_ENV_VARIABLE": "UP_API_TOKEN_KAIT",
        "ACCOUNT_NAME": "Groceries",
        "WEEKS_PER_WAGE_CYCLE": 1,
        "WAGE_CYCLE_START": date(2021, 2, 22),
        "DEPOSITED": (MONDAY, SIX_AM),
        "WEEKLY_BUDGET": Decimal(62.50),
    },
}


def get_config(user, key):
    """Get the config item for the user."""
    if user not in user_config:
        raise ValueError(f"Received unknown user: `{user}`")
    if key not in user_config[user]:
        raise ValueError(f"Received unknown key: `{key}`")
    return user_config[user][key]


def get_balance(user):
    """Return the balance of the groceries account for the user."""
    account_name = get_config(user, "ACCOUNT_NAME")
    groceries_account = None
    with up_auth.user(get_config(user, "API_TOKEN_ENV_VARIABLE")):
        accounts = Account.get_list()
    for account in accounts:
        if account_name in account.name:
            groceries_account = account
            break
    if groceries_account is None:
        raise ValueError(f"Could not find account `{account_name}` for user `{user}`")
    return Decimal(groceries_account.balance["value"])


def get_weekday(date_time: datetime, weekday: int, time_of_day: time):
    """Get the date of the weekday of this week."""
    day_of_week_from_sunday = date_time.isoweekday() % 7
    return date_time + relativedelta.relativedelta(
        days=weekday - day_of_week_from_sunday,
        hour=time_of_day.hour,
        minute=time_of_day.minute,
        second=time_of_day.second,
        microsecond=time_of_day.microsecond,
    )


def get_week_modifier(user, date_time):
    """Return the week number for the user."""
    num_weeks = get_config(user, "WEEKS_PER_WAGE_CYCLE")
    start_datetime = datetime.combine(
        get_config(user, "WAGE_CYCLE_START"), get_config(user, "DEPOSITED")[1]
    )
    return num_weeks - (int((date_time - start_datetime).days / 7) % num_weeks)


def calculate_subtraction(user, date_time=None):
    """Determine how much to subtract from the user's account."""
    if date_time is None:
        date_time = datetime.now()
    day_of_week_deposited, time_deposited = get_config(user, "DEPOSITED")
    sunday_midnight = get_weekday(date_time, SUNDAY, MIDNIGHT)
    deposit_datetime = get_weekday(date_time, day_of_week_deposited, time_deposited)
    modifier = get_week_modifier(user, date_time)
    if deposit_datetime > date_time > sunday_midnight:
        modifier -= 1
    return get_config(user, "WEEKLY_BUDGET") * modifier


def main():
    """Get the groceries."""
    users = ["nat", "kait"]
    balance = 0
    for user in users:
        balance += get_balance(user) - calculate_subtraction(user)
    return f"Balance remaining: {balance}"


if __name__ == "__main__":
    main()
