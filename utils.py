"""
utils.py

Providing small, reusable helper functions that support the Requisition
Management System: input validation, ID generation, and text formatting.
Keeping these functions here so that both the business-logic layer
(requisition.py) and the GUI layer (gui.py) can reuse them without
duplicating code.
"""

from datetime import datetime


def is_valid_date(date_str):
    """Checking whether the given string is a valid date in YYYY-MM-DD format."""
    if not date_str or not date_str.strip():
        return False
    try:
        datetime.strptime(date_str.strip(), "%Y-%m-%d")
        return True
    except ValueError:
        return False


def is_non_empty(value):
    """Checking that a given text field is not empty or made up of only spaces."""
    return bool(value and value.strip())


def is_valid_cost(cost_str):
    """Checking that the entered cost is a valid, non-negative number."""
    try:
        cost = float(cost_str)
        return cost >= 0
    except (ValueError, TypeError):
        return False


def generate_requisition_id(counter):
    """Generating a unique, zero-padded Requisition ID from a running counter."""
    return f"REQ-{counter:04d}"


def generate_approval_reference(staff_id, requisition_id):
    """
    Generating an approval reference from the Staff ID and the last
    three digits of the Requisition ID.

    Example:
        Staff ID: S001
        Requisition ID: REQ-0001
        Approval Reference: S001001
    """
    digits = "".join(filter(str.isdigit, requisition_id))
    return f"{staff_id}{digits[-3:]}"


def format_currency(amount):
    """Formatting a numeric amount into a readable currency string, e.g. $1,234.50."""
    return f"${amount:,.2f}"


def get_today_string():
    """Returning today's date, formatted as YYYY-MM-DD, for default form values."""
    return datetime.now().strftime("%Y-%m-%d")