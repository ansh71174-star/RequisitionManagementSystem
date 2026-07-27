"""
requisition.py

Defining the core business logic for the Requisition Management System.

Containing two classes:
    - Requisition: representing a single requisition and everything it
      knows how to do to itself (calculating its total, approving itself,
      responding to a manager's decision, and displaying itself).
    - RequisitionManager: owning the full collection of requisitions and
      coordinating creation, searching, the approval workflow, and
      statistics, so the GUI never touches business rules directly.

Keeping all business logic inside this module, separate from utils.py
(shared helpers) and gui.py (presentation only).
"""

from utils import (
    generate_requisition_id,
    generate_approval_reference,
    format_currency,
)

# Defining the auto-approval threshold as a module-level constant so it is
# easy to find and adjust in one place
AUTO_APPROVAL_LIMIT = 500.0


class Requisition:
    """
    Representing one requisition submitted by a staff member.

    Storing its own date, staff ID, staff name, items, total cost,
    status, and approval reference, and knowing how to calculate its
    total, approve itself automatically, respond to a manager's
    decision, and display itself.
    """

    def __init__(self, requisition_id, date, staff_id, staff_name, items):
        """Initialising every shared data field for a single requisition."""
        self.requisition_id = requisition_id
        self.date = date
        self.staff_id = staff_id
        self.staff_name = staff_name
        self.items = items

        # Calculating the starting total immediately from the items given
        self.total_cost = self.calculate_total()

        # Starting every requisition as Pending until it is either
        # auto-approved or responded to by a manager
        self.status = "Pending"
        self.approval_reference = "Not Available"

    def calculate_total(self):
        """Calculating the total cost of all items on this requisition."""
        return sum(item["cost"] for item in self.items)

    def approve_requisition(self):
        """
        Deciding whether this requisition is auto-approved, based on the
        AUTO_APPROVAL_LIMIT business rule: totals under the limit are
        approved immediately with a generated approval reference, and
        totals at or above the limit are left Pending for a manager.
        """
        self.total_cost = self.calculate_total()

        if self.total_cost < AUTO_APPROVAL_LIMIT:
            self.status = "Approved"
            self.approval_reference = generate_approval_reference(
                self.staff_id,
                self.requisition_id,
            )
        else:
            self.status = "Pending"
            self.approval_reference = "Not Available"

        return self.status

    def respond_requisition(self, decision):
        """
        Applying a manager's decision ("Approve", "Not Approve"/"Reject",
        or anything else meaning leave it Pending) to this requisition and
        updating its status and approval reference accordingly.
        """
        decision = decision.strip().lower()

        if decision == "approve":
            self.status = "Approved"
            self.approval_reference = generate_approval_reference(
                self.staff_id,
                self.requisition_id,
            )
        elif decision in ("not approve", "reject"):
            self.status = "Not Approved"
            self.approval_reference = "Not Available"
        else:
            self.status = "Pending"
            self.approval_reference = "Not Available"

        return self.status

    def display_requisition(self):
        """Building a human-readable, multi-line summary of this requisition."""
        return (
            f"Date: {self.date}\n"
            f"Requisition ID: {self.requisition_id}\n"
            f"Staff ID: {self.staff_id}\n"
            f"Staff Name: {self.staff_name}\n"
            f"Total: {format_currency(self.total_cost)}\n"
            f"Status: {self.status}\n"
            f"Approval Reference Number: {self.approval_reference}"
        )

    def to_row(self):
        """Returning this requisition as a tuple, ready for a Treeview row."""
        return (
            self.requisition_id,
            self.date,
            self.staff_id,
            self.staff_name,
            format_currency(self.total_cost),
            self.status,
            self.approval_reference,
        )


class RequisitionManager:
    """
    Owning and managing the complete collection of requisitions:
    creating them, searching them, running the approval workflow, and
    producing statistics — every operation the GUI needs, without the
    GUI ever manipulating a Requisition's fields directly.
    """

    def __init__(self):
        """Starting with an empty requisition list and a fresh ID counter."""
        self.requisitions = []
        self._id_counter = 1

    def add_requisition(self, date, staff_id, staff_name, items):
        """
        Creating a new Requisition from the given staff details and item
        list, generating its unique ID, running the auto-approval check,
        storing it, and returning the finished requisition object.
        """
        requisition_id = generate_requisition_id(self._id_counter)
        self._id_counter += 1

        requisition = Requisition(
            requisition_id,
            date,
            staff_id,
            staff_name,
            items,
        )

        # Deciding immediately whether the new requisition is auto-approved
        requisition.approve_requisition()

        self.requisitions.append(requisition)
        return requisition

    def get_pending_requisitions(self):
        """Returning only the requisitions currently awaiting a manager's decision."""
        return [
            req
            for req in self.requisitions
            if req.status == "Pending"
        ]

    def get_all_requisitions(self):
        """Returning every requisition that has ever been submitted."""
        return self.requisitions

    def find_by_id(self, requisition_id):
        """Locating a single requisition by its unique ID, or None if not found."""
        for req in self.requisitions:
            if req.requisition_id == requisition_id:
                return req
        return None

    def search_by_staff_id(self, staff_id):
        """Finding every requisition submitted by a given Staff ID (case-insensitive)."""
        staff_id = staff_id.strip().lower()
        return [
            req
            for req in self.requisitions
            if req.staff_id.lower() == staff_id
        ]

    def respond_to_requisition(self, requisition_id, decision):
        """
        Looking up a requisition by ID and applying a manager's decision
        to it, returning the updated requisition or None if it could not
        be found.
        """
        requisition = self.find_by_id(requisition_id)
        if requisition is None:
            return None

        requisition.respond_requisition(decision)
        return requisition

    def requisition_statistics(self):
        """
        Counting how many requisitions have been submitted, approved,
        left pending, and not approved, and returning those counts as a
        dictionary.
        """
        stats = {
            "Submitted": len(self.requisitions),
            "Approved": 0,
            "Pending": 0,
            "Not Approved": 0,
        }

        for req in self.requisitions:
            if req.status in stats:
                stats[req.status] += 1

        return stats