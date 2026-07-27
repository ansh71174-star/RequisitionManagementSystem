# Requisition Management System

A complete, object-oriented Python desktop application for submitting,
reviewing, and tracking staff requisitions, built with **Tkinter**.

## Project Overview

Staff members submit requisitions made up of one or more priced items.
Requisitions with a total **under $500** are approved automatically;
anything **$500 or more** is held as **Pending** until a manager
explicitly approves or rejects it. The system tracks every requisition
ever submitted and reports live statistics (Submitted / Approved /
Pending / Not Approved) as decisions are made.

## Objectives

- Encapsulate requisition data and behaviour inside a class-based design.
- Separate business logic (`requisition.py`, `utils.py`) from the
  presentation layer (`gui.py`), so the interface never manipulates
  requisition data directly.
- Provide an event-driven, Tkinter-based GUI covering the full workflow:
  submission, manager review, statistics, search, and history.
- Demonstrate the design and the business rules through console-based
  test data seeded on startup.

## File Structure

```text
RequisitionSystem/
│── main.py          # Entry point: seeds test data, launches the GUI
│── requisition.py   # Requisition + RequisitionManager classes (business logic)
│── gui.py           # RequisitionApp class (Tkinter/ttk interface only)
│── utils.py         # Validation, ID generation, and formatting helpers
│── README.md         # This file
```

## Requirements

- Python 3.8+
- Tkinter (included with most standard Python installations)

No third-party packages are required.

## How to Run

From inside the `RequisitionSystem` folder:

```bash
python main.py
```

On startup, the console prints five seeded test requisitions (covering a
total below $500, a total above $500, an explicitly approved
requisition, a requisition left pending, and an explicitly rejected
requisition) along with statistics after each step. The GUI then opens,
pre-loaded with that same data.

## OOP Design

- **`Requisition`** (in `requisition.py`) represents a single requisition.
  It stores its own date, staff ID, staff name, items, total cost,
  status, and approval reference, and knows how to calculate its total,
  approve itself automatically, respond to a manager's decision, and
  display itself.
- **`RequisitionManager`** (in `requisition.py`) owns the full list of
  requisitions and handles creation, searching, the approval workflow,
  and statistics — every operation the GUI needs, without the GUI ever
  touching business rules directly.
- **`RequisitionApp`** (in `gui.py`) builds every Tkinter/ttk widget and
  only calls methods on `RequisitionManager` / `Requisition` in response
  to button clicks and selections.
- **`utils.py`** holds small, shared helper functions used by both the
  business logic and the GUI (validation, ID generation, formatting).

This keeps the project modular: the GUI could be swapped for a web
front end or a command-line interface without touching a single line of
business logic.

## Business Rule

- Total cost **under $500** → status automatically set to **Approved**,
  and an Approval Reference Number is generated.
- Total cost **$500 or more** → status set to **Pending**, with the
  Approval Reference shown as **Not Available** until a manager responds.
- A manager can respond to a pending requisition with **Approve** or
  **Not Approve**, which updates its status and statistics immediately.

## Features

- Add, remove, and clear items while building a requisition.
- Live running total as items are added or removed.
- Submit a requisition and see its auto-decided status immediately.
- Manager panel listing only currently pending requisitions, with
  confirmation prompts before approving or rejecting.
- Live statistics (Submitted / Approved / Pending / Not Approved).
- Search requisition history by Staff ID, or browse the full history.
- Click any historical requisition to view its full details.
- Reset the form or exit the application, both with confirmation.

## GUI Overview

- **Staff Information** — Date, Staff ID, Staff Name
- **Item Entry** — add/remove/clear items, shown in a table
- **Requisition** — calculate total, submit, clear form, reset, exit
- **Manager Section** — review and approve/reject pending requisitions
- **Statistics** — live counts of Submitted / Approved / Pending / Not Approved
- **Search + Requisition History** — search by Staff ID, browse every
  requisition ever submitted, and view full details of any selected entry

## Validation

The form validates: empty Staff ID, empty Staff Name, empty or
incorrectly formatted Date, empty item name, non-numeric cost, negative
cost, and submitting without any items — with clear, specific error
message boxes for each case.

## Testing

`main.py` seeds five requisitions directly through `RequisitionManager`
before the GUI opens, covering:

1. A total **below $500** (auto-approved).
2. A total **above $500** (left pending).
3. A total above $500 that is **explicitly approved** by a manager.
4. A total above $500 that is **left pending** (no manager action).
5. A total above $500 that is **explicitly rejected** by a manager.

Statistics are printed to the console after every step, and the same
seeded data is visible in the GUI once it opens — so the GUI and the
console tests can be cross-checked against each other.

## Future Improvements

- Persisting requisitions to a file or database between runs.
- Exporting requisition history to CSV.
- Role-based login separating staff and manager views.

## Assessment Mapping

| Rubric criterion | Where it's demonstrated |
|---|---|
| Programming logic & algorithms | `Requisition.approve_requisition`, `respond_requisition` |
| Object-oriented design | `Requisition` / `RequisitionManager` classes, encapsulated state |
| System functionality & statistics | `requisition_statistics`, live GUI statistics panel |
| Code execution, testing & debugging | `main.py`'s `run_console_tests` |
| SDLC application | Documented separately in the Assessment 2 report |

## Author

Submitted as part of Assessment 2 (BACT7501) — Software Development Project.

## GitHub

Add your public repository link here once created, e.g.:
`https://github.com/<your-username>/requisition-management-system`