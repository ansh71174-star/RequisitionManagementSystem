"""
main.py

Serving as the entry point for the Requisition Management System.

Creating a RequisitionManager, seeding it with at least five test
requisitions (covering totals below and above $500, an explicitly
approved requisition, a pending requisition, and an explicitly
rejected requisition), printing statistics after each operation, and
then launching the Tkinter GUI so the application is running as soon
as this file opens.
"""

import tkinter as tk

from requisition import RequisitionManager
from gui import RequisitionApp


def _print_section(title):
    """Printing a consistent banner so each test step is easy to read in the console."""
    print("=" * 60)
    print(title)
    print("=" * 60)


def run_console_tests(manager):
    """
    Creating five sample requisitions directly through the business
    layer, demonstrating every required status, and printing statistics
    after each operation. Running before the GUI opens, purely for
    console-based testing.
    """
    _print_section("Running startup test requisitions")

    # 1) Creating a requisition with a total BELOW $500 -> auto-approved
    r1 = manager.add_requisition(
        date="2026-07-01",
        staff_id="S001",
        staff_name="Alice Johnson",
        items=[{"name": "Printer Paper", "cost": 45.00}, {"name": "Pens", "cost": 15.50}],
    )
    print(r1.display_requisition())
    print("Statistics:", manager.requisition_statistics(), "\n")

    # 2) Creating a requisition with a total ABOVE $500 -> left pending
    r2 = manager.add_requisition(
        date="2026-07-02",
        staff_id="S002",
        staff_name="Brian Lee",
        items=[{"name": "Office Chair", "cost": 350.00}, {"name": "Desk Lamp", "cost": 220.00}],
    )
    print(r2.display_requisition())
    print("Statistics:", manager.requisition_statistics(), "\n")

    # 3) Creating a requisition that ends up EXPLICITLY approved by a manager
    r3 = manager.add_requisition(
        date="2026-07-03",
        staff_id="S003",
        staff_name="Carla Mendes",
        items=[{"name": "Laptop Stand", "cost": 300.00}, {"name": "Webcam", "cost": 250.00}],
    )
    manager.respond_to_requisition(r3.requisition_id, "Approve")
    print(r3.display_requisition())
    print("Statistics:", manager.requisition_statistics(), "\n")

    # 4) Creating a requisition that is left PENDING (manager takes no action)
    r4 = manager.add_requisition(
        date="2026-07-04",
        staff_id="S004",
        staff_name="Derek Osei",
        items=[{"name": "Conference Table", "cost": 900.00}],
    )
    print(r4.display_requisition())
    print("Statistics:", manager.requisition_statistics(), "\n")

    # 5) Creating a requisition that gets explicitly REJECTED by a manager
    r5 = manager.add_requisition(
        date="2026-07-05",
        staff_id="S005",
        staff_name="Elena Petrova",
        items=[{"name": "Gaming Chair", "cost": 700.00}],
    )
    manager.respond_to_requisition(r5.requisition_id, "Not Approve")
    print(r5.display_requisition())
    print("Statistics:", manager.requisition_statistics(), "\n")

    _print_section(f"Final statistics before launching the GUI: {manager.requisition_statistics()}")


def main():
    """Building the manager, running the seed/test data, and starting the GUI main loop."""
    manager = RequisitionManager()
    run_console_tests(manager)

    root = tk.Tk()
    RequisitionApp(root, manager=manager)
    root.mainloop()


if __name__ == "__main__":
    main()