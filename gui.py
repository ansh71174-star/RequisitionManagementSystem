"""
gui.py

Building the complete Tkinter graphical user interface for the
Requisition Management System.

Containing ONLY presentation and event-handling code. Every piece of
business logic (calculating totals, generating IDs, deciding approval
status, gathering statistics, searching requisitions, and responding to
manager actions) is being delegated to the RequisitionManager and
Requisition classes defined in requisition.py. This module is simply
wiring up widgets and calling those class methods, keeping a clear
separation between the graphical interface and the business logic.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from requisition import RequisitionManager
from utils import (
    is_valid_date,
    is_non_empty,
    is_valid_cost,
    get_today_string,
)

# Centralising the colour palette so every section stays visually consistent
COLOR_BACKGROUND = "#FFFFFF"
COLOR_TITLE = "#0B3D91"
COLOR_ACCENT = "#1A5276"
COLOR_FRAME_BG = "#F4F6F7"


class RequisitionApp:
    """
    Representing the complete graphical user interface for the
    Requisition Management System.
    """

    def __init__(self, root, manager=None):
        """
        Setting up the main application window, creating the manager,
        configuring styles, building the interface, and loading any
        existing requisition data.
        """
        self.root = root
        self.root.title("Requisition Management System")

        # Setting a larger window size for a more professional interface
        self.root.geometry("1400x850")
        self.root.minsize(1200, 750)
        self.root.configure(background=COLOR_BACKGROUND)

        # Using an existing manager when one is being supplied, so main.py
        # can hand over the manager it already seeded with test data
        self.manager = manager if manager is not None else RequisitionManager()

        # Holding the items currently being entered for the requisition
        # that is being built in the form
        self.current_items = []

        # Configuring the graphical styles
        self._configure_styles()

        # Building every section of the graphical interface
        self._build_layout()

        # Refreshing every section with the current data
        self.refresh_all()

    # ------------------------------------------------------------------
    # Styling
    # ------------------------------------------------------------------
    def _configure_styles(self):
        """Configuring the ttk styles used across the entire interface."""
        style = ttk.Style()

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass  # Falling back to the default theme if 'clam' is unavailable

        style.configure("TFrame", background=COLOR_BACKGROUND)
        style.configure("TLabel", background=COLOR_BACKGROUND, font=("Segoe UI", 10))
        style.configure(
            "TLabelframe",
            background=COLOR_FRAME_BG,
            bordercolor="#B7C4CE",
        )
        style.configure(
            "TLabelframe.Label",
            background=COLOR_FRAME_BG,
            font=("Segoe UI", 11, "bold"),
            foreground=COLOR_ACCENT,
        )

        style.configure(
            "Title.TLabel",
            background=COLOR_BACKGROUND,
            font=("Segoe UI", 22, "bold"),
            foreground=COLOR_TITLE,
        )
        style.configure(
            "Subtitle.TLabel",
            background=COLOR_BACKGROUND,
            font=("Segoe UI", 10),
            foreground="#5D6D7E",
        )
        style.configure(
            "Header.TLabel",
            background=COLOR_FRAME_BG,
            font=("Segoe UI", 11, "bold"),
        )
        style.configure(
            "Stat.TLabel",
            background=COLOR_FRAME_BG,
            font=("Segoe UI", 16, "bold"),
            foreground=COLOR_ACCENT,
        )
        style.configure(
            "StatCaption.TLabel",
            background=COLOR_FRAME_BG,
            font=("Segoe UI", 9),
            foreground="#5D6D7E",
        )
        style.configure(
            "Total.TLabel",
            background=COLOR_FRAME_BG,
            font=("Segoe UI", 14, "bold"),
            foreground=COLOR_ACCENT,
        )

        # Giving every button a consistent, roomier footprint
        style.configure("TButton", font=("Segoe UI", 10), padding=6)
        style.configure(
            "Accent.TButton",
            font=("Segoe UI", 10, "bold"),
        )

        style.configure("Treeview", rowheight=28, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

    # ------------------------------------------------------------------
    # Layout construction
    # ------------------------------------------------------------------
    def _build_layout(self):
        """
        Building the complete application layout: the title banner and
        the left/right column arrangement that holds every section.
        """
        container = ttk.Frame(self.root, padding=14)
        container.grid(row=0, column=0, sticky="nsew")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        container.grid_columnconfigure(0, weight=3)
        container.grid_columnconfigure(1, weight=2)
        container.grid_rowconfigure(1, weight=1)

        # Building the title banner across the top of the window
        self._build_title_banner(container)

        left_column = ttk.Frame(container)
        left_column.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        left_column.grid_columnconfigure(0, weight=1)

        right_column = ttk.Frame(container)
        right_column.grid(row=1, column=1, sticky="nsew")
        right_column.grid_columnconfigure(0, weight=1)
        right_column.grid_rowconfigure(2, weight=1)

        # Building each labelled section, passing in the frame it should live in
        self._build_staff_section(left_column)
        self._build_item_section(left_column)
        self._build_requisition_section(left_column)
        self._build_manager_section(left_column)

        self._build_statistics_section(right_column)
        self._build_search_section(right_column)
        self._build_history_section(right_column)

    def _build_title_banner(self, parent):
        """Building the professional title banner shown at the top of the window."""
        banner = ttk.Frame(parent)
        banner.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 16))
        banner.grid_columnconfigure(0, weight=1)

        title = ttk.Label(
            banner,
            text="REQUISITION MANAGEMENT SYSTEM",
            style="Title.TLabel",
            anchor="center",
        )
        title.grid(row=0, column=0, sticky="ew")

        subtitle = ttk.Label(
            banner,
            text="Submit, review, and track staff requisitions",
            style="Subtitle.TLabel",
            anchor="center",
        )
        subtitle.grid(row=1, column=0, sticky="ew")

    # ------------------------------------------------------------------
    # Staff Information section
    # ------------------------------------------------------------------
    def _build_staff_section(self, parent):
        """Building the Staff Information entry section: Date, Staff ID, Staff Name."""
        frame = ttk.LabelFrame(parent, text="Staff Information", padding=12)
        frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_columnconfigure(3, weight=1)

        ttk.Label(frame, text="Date (YYYY-MM-DD):").grid(row=0, column=0, sticky="w", padx=4, pady=6)
        self.date_entry = ttk.Entry(frame)
        self.date_entry.insert(0, get_today_string())  # Pre-filling today's date
        self.date_entry.grid(row=0, column=1, sticky="ew", padx=4, pady=6)

        ttk.Label(frame, text="Staff ID:").grid(row=0, column=2, sticky="w", padx=4, pady=6)
        self.staff_id_entry = ttk.Entry(frame)
        self.staff_id_entry.grid(row=0, column=3, sticky="ew", padx=4, pady=6)

        ttk.Label(frame, text="Staff Name:").grid(row=1, column=0, sticky="w", padx=4, pady=6)
        self.staff_name_entry = ttk.Entry(frame)
        self.staff_name_entry.grid(row=1, column=1, columnspan=3, sticky="ew", padx=4, pady=6)

    # ------------------------------------------------------------------
    # Item Entry section
    # ------------------------------------------------------------------
    def _build_item_section(self, parent):
        """Building the Item Entry section: item fields, buttons, and a Treeview list."""
        frame = ttk.LabelFrame(parent, text="Item Entry", padding=12)
        frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_columnconfigure(3, weight=1)

        ttk.Label(frame, text="Item Name:").grid(row=0, column=0, sticky="w", padx=4, pady=6)
        self.item_name_entry = ttk.Entry(frame)
        self.item_name_entry.grid(row=0, column=1, sticky="ew", padx=4, pady=6)

        ttk.Label(frame, text="Cost:").grid(row=0, column=2, sticky="w", padx=4, pady=6)
        self.item_cost_entry = ttk.Entry(frame)
        self.item_cost_entry.grid(row=0, column=3, sticky="ew", padx=4, pady=6)

        button_row = ttk.Frame(frame)
        button_row.grid(row=1, column=0, columnspan=4, sticky="w", pady=(4, 10))
        ttk.Button(button_row, text="Add Item", width=18, command=self.add_item).pack(side="left", padx=3)
        ttk.Button(button_row, text="Remove Selected", width=18, command=self.remove_selected_item).pack(side="left", padx=3)
        ttk.Button(button_row, text="Clear Items", width=18, command=self.clear_items).pack(side="left", padx=3)

        # Displaying entered items inside a Treeview table with a scrollbar
        tree_frame = ttk.Frame(frame)
        tree_frame.grid(row=2, column=0, columnspan=4, sticky="nsew")
        frame.grid_rowconfigure(2, weight=1)

        columns = ("item", "cost")
        self.item_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=5)
        self.item_tree.heading("item", text="Item Name")
        self.item_tree.heading("cost", text="Cost")
        self.item_tree.column("item", width=220)
        self.item_tree.column("cost", width=110, anchor="center")

        item_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.item_tree.yview)
        self.item_tree.configure(yscrollcommand=item_scroll.set)
        self.item_tree.pack(side="left", fill="both", expand=True)
        item_scroll.pack(side="right", fill="y")

    # ------------------------------------------------------------------
    # Requisition section
    # ------------------------------------------------------------------
    def _build_requisition_section(self, parent):
        """Building the Requisition section: total calculation and submission."""
        frame = ttk.LabelFrame(parent, text="Requisition", padding=12)
        frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))

        button_row = ttk.Frame(frame)
        button_row.pack(side="top", fill="x")
        ttk.Button(button_row, text="Calculate Total", width=16, command=self.calculate_total).pack(side="left", padx=3)
        ttk.Button(button_row, text="Submit Requisition", width=18, style="Accent.TButton", command=self.submit_requisition).pack(side="left", padx=3)
        ttk.Button(button_row, text="Clear Form", width=12, command=self.clear_form).pack(side="left", padx=3)
        ttk.Button(button_row, text="Reset", width=10, command=self.reset_all).pack(side="left", padx=3)
        ttk.Button(button_row, text="Exit", width=10, command=self.exit_app).pack(side="left", padx=3)

        # Making the current total large and clearly visible
        self.total_label = ttk.Label(frame, text="Current Total: $0.00", style="Total.TLabel")
        self.total_label.pack(side="top", anchor="e", pady=(10, 0))

    # ------------------------------------------------------------------
    # Manager section
    # ------------------------------------------------------------------
    def _build_manager_section(self, parent):
        """Building the Manager section: reviewing and responding to pending requisitions."""
        frame = ttk.LabelFrame(parent, text="Manager Section — Pending Requisitions", padding=12)
        frame.grid(row=3, column=0, sticky="nsew", pady=(0, 10))
        parent.grid_rowconfigure(3, weight=1)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        button_row = ttk.Frame(frame)
        button_row.grid(row=0, column=0, sticky="w", pady=(0, 8))
        ttk.Button(button_row, text="Approve", width=14, command=self.approve_selected).pack(side="left", padx=3)
        ttk.Button(button_row, text="Reject", width=14, command=self.reject_selected).pack(side="left", padx=3)
        ttk.Button(button_row, text="Refresh List", width=14, command=self.refresh_manager_list).pack(side="left", padx=3)

        tree_frame = ttk.Frame(frame)
        tree_frame.grid(row=1, column=0, sticky="nsew")

        columns = ("id", "staff_id", "staff_name", "total")
        self.manager_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=6)
        self.manager_tree.heading("id", text="Requisition ID")
        self.manager_tree.heading("staff_id", text="Staff ID")
        self.manager_tree.heading("staff_name", text="Staff Name")
        self.manager_tree.heading("total", text="Total")
        for col in columns:
            self.manager_tree.column(col, width=110, anchor="center")

        manager_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.manager_tree.yview)
        self.manager_tree.configure(yscrollcommand=manager_scroll.set)
        self.manager_tree.pack(side="left", fill="both", expand=True)
        manager_scroll.pack(side="right", fill="y")

    # ------------------------------------------------------------------
    # Statistics section
    # ------------------------------------------------------------------
    def _build_statistics_section(self, parent):
        """Building the Statistics section, refreshing automatically after every action."""
        frame = ttk.LabelFrame(parent, text="Statistics", padding=12)
        frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        for i in range(4):
            frame.grid_columnconfigure(i, weight=1)

        self.stat_labels = {}
        stat_names = ["Submitted", "Approved", "Pending", "Not Approved"]
        for i, name in enumerate(stat_names):
            value_label = ttk.Label(frame, text="0", style="Stat.TLabel", anchor="center")
            value_label.grid(row=0, column=i, sticky="ew", padx=4)
            caption_label = ttk.Label(frame, text=name, style="StatCaption.TLabel", anchor="center")
            caption_label.grid(row=1, column=i, sticky="ew", padx=4)
            self.stat_labels[name] = value_label

    # ------------------------------------------------------------------
    # Search section
    # ------------------------------------------------------------------
    def _build_search_section(self, parent):
        """Building the search-by-Staff-ID section above the requisition history."""
        frame = ttk.LabelFrame(parent, text="Search by Staff ID", padding=12)
        frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        frame.grid_columnconfigure(0, weight=1)

        self.search_entry = ttk.Entry(frame)
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        ttk.Button(frame, text="Search", width=10, command=self.search_by_staff).grid(row=0, column=1, padx=3)
        ttk.Button(frame, text="Show All", width=10, command=self.refresh_history).grid(row=0, column=2, padx=3)

    # ------------------------------------------------------------------
    # Requisition History section
    # ------------------------------------------------------------------
    def _build_history_section(self, parent):
        """Building the Requisition History section, listing every requisition ever made."""
        frame = ttk.LabelFrame(parent, text="Requisition History", padding=12)
        frame.grid(row=2, column=0, sticky="nsew")
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        columns = ("id", "date", "staff_id", "staff_name", "total", "status", "approval")
        headings = {
            "id": "Requisition ID",
            "date": "Date",
            "staff_id": "Staff ID",
            "staff_name": "Staff Name",
            "total": "Total",
            "status": "Status",
            "approval": "Approval Ref",
        }

        self.history_tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            self.history_tree.heading(col, text=headings[col])
            self.history_tree.column(col, width=100, anchor="center")

        v_scroll = ttk.Scrollbar(frame, orient="vertical", command=self.history_tree.yview)
        h_scroll = ttk.Scrollbar(frame, orient="horizontal", command=self.history_tree.xview)
        self.history_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        self.history_tree.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")

        # Displaying the full details of whichever requisition is selected
        self.detail_label = ttk.Label(
            frame,
            text="Select a requisition to view its full details.",
            wraplength=380,
            justify="left",
        )
        self.detail_label.grid(row=2, column=0, columnspan=2, sticky="w", pady=(10, 0))
        self.history_tree.bind("<<TreeviewSelect>>", self.show_selected_details)

    # ------------------------------------------------------------------
    # Item Entry event handlers
    # ------------------------------------------------------------------
    def add_item(self):
        """Validating the item fields and adding a new item to the current requisition."""
        name = self.item_name_entry.get()
        cost_str = self.item_cost_entry.get()

        if not is_non_empty(name):
            messagebox.showerror("Missing Item Name", "Please enter a name for the item before adding it.")
            return
        if not is_valid_cost(cost_str):
            messagebox.showerror(
                "Invalid Cost",
                "Please enter a valid, non-negative numeric cost (e.g. 49.99).",
            )
            return

        cost = float(cost_str)
        self.current_items.append({"name": name.strip(), "cost": cost})
        self.item_tree.insert("", "end", values=(name.strip(), f"${cost:,.2f}"))

        # Clearing the input fields so the user can quickly add the next item
        self.item_name_entry.delete(0, tk.END)
        self.item_cost_entry.delete(0, tk.END)
        self.calculate_total()

    def remove_selected_item(self):
        """Removing whichever item row is currently selected in the item Treeview."""
        selected = self.item_tree.selection()
        if not selected:
            messagebox.showwarning("No Item Selected", "Please select an item in the list to remove it.")
            return

        for row_id in selected:
            index = self.item_tree.index(row_id)
            del self.current_items[index]
            self.item_tree.delete(row_id)

        self.calculate_total()

    def clear_items(self):
        """Clearing every item currently added to the requisition being built."""
        self.current_items = []
        self.item_tree.delete(*self.item_tree.get_children())
        self.calculate_total()

    # ------------------------------------------------------------------
    # Requisition event handlers
    # ------------------------------------------------------------------
    def calculate_total(self):
        """Calculating and displaying the running total of the current item list."""
        total = sum(item["cost"] for item in self.current_items)
        self.total_label.config(text=f"Current Total: ${total:,.2f}")
        return total

    def submit_requisition(self):
        """Validating the full form and submitting a new requisition to the manager."""
        date = self.date_entry.get()
        staff_id = self.staff_id_entry.get()
        staff_name = self.staff_name_entry.get()

        if not is_valid_date(date):
            messagebox.showerror(
                "Invalid Date",
                "Please enter the date in YYYY-MM-DD format (e.g. 2026-07-26).",
            )
            return
        if not is_non_empty(staff_id):
            messagebox.showerror("Missing Staff ID", "Please enter the Staff ID before submitting.")
            return
        if not is_non_empty(staff_name):
            messagebox.showerror("Missing Staff Name", "Please enter the Staff Name before submitting.")
            return
        if not self.current_items:
            messagebox.showerror(
                "No Items Added",
                "Please add at least one item before submitting the requisition.",
            )
            return

        new_requisition = self.manager.add_requisition(
            date=date.strip(),
            staff_id=staff_id.strip(),
            staff_name=staff_name.strip(),
            items=self.current_items,
        )

        messagebox.showinfo(
            "Requisition Submitted Successfully",
            f"Requisition {new_requisition.requisition_id} has been submitted.\n"
            f"Current status: {new_requisition.status}",
        )

        self.clear_form()
        self.refresh_all()

    # ------------------------------------------------------------------
    # Manager event handlers
    # ------------------------------------------------------------------
    def approve_selected(self):
        """Confirming with the user, then approving the selected pending requisition."""
        self._respond_to_selected(
            decision="Approve",
            confirm_message="Are you sure you want to approve this requisition?",
        )

    def reject_selected(self):
        """Confirming with the user, then rejecting the selected pending requisition."""
        self._respond_to_selected(
            decision="Not Approve",
            confirm_message="Are you sure you want to reject this requisition?",
        )

    def _respond_to_selected(self, decision, confirm_message):
        """Applying the manager's decision to the selected requisition after confirming."""
        selected = self.manager_tree.selection()
        if not selected:
            messagebox.showwarning(
                "No Requisition Selected",
                "Please select a pending requisition to respond to.",
            )
            return

        if not messagebox.askyesno("Confirm Decision", confirm_message):
            return

        values = self.manager_tree.item(selected[0], "values")
        requisition_id = values[0]

        updated = self.manager.respond_to_requisition(requisition_id, decision)
        if updated is None:
            messagebox.showerror("Requisition Not Found", "That requisition could not be located.")
            return

        messagebox.showinfo(
            "Decision Recorded",
            f"Requisition {updated.requisition_id} is now marked as {updated.status}.",
        )
        self.refresh_all()

    def refresh_manager_list(self):
        """Refreshing the Manager section so it only shows currently pending requisitions."""
        self.manager_tree.delete(*self.manager_tree.get_children())
        for requisition in self.manager.get_pending_requisitions():
            self.manager_tree.insert(
                "",
                "end",
                values=(
                    requisition.requisition_id,
                    requisition.staff_id,
                    requisition.staff_name,
                    f"${requisition.total_cost:,.2f}",
                ),
            )

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    def refresh_statistics(self):
        """Recomputing statistics from the manager and updating every stat label."""
        stats = self.manager.requisition_statistics()
        for name, label in self.stat_labels.items():
            label.config(text=str(stats.get(name, 0)))

    # ------------------------------------------------------------------
    # Search / History
    # ------------------------------------------------------------------
    def search_by_staff(self):
        """Filtering the Requisition History to show only one staff member's requisitions."""
        staff_id = self.search_entry.get()
        if not is_non_empty(staff_id):
            messagebox.showwarning("Missing Staff ID", "Please enter a Staff ID to search for.")
            return

        results = self.manager.search_by_staff_id(staff_id)
        self.history_tree.delete(*self.history_tree.get_children())
        for requisition in results:
            self.history_tree.insert("", "end", values=requisition.to_row())

        if not results:
            messagebox.showinfo("No Results", "No requisitions were found for that Staff ID.")

    def refresh_history(self):
        """Refreshing the Requisition History Treeview with every stored requisition."""
        self.search_entry.delete(0, tk.END)
        self.history_tree.delete(*self.history_tree.get_children())
        for requisition in self.manager.get_all_requisitions():
            self.history_tree.insert("", "end", values=requisition.to_row())

    def show_selected_details(self, event=None):
        """Displaying full details for whichever requisition is selected in the history list."""
        selected = self.history_tree.selection()
        if not selected:
            return
        values = self.history_tree.item(selected[0], "values")
        requisition_id = values[0]
        requisition = self.manager.find_by_id(requisition_id)
        if requisition:
            self.detail_label.config(text=requisition.display_requisition())

    # ------------------------------------------------------------------
    # Form / global reset handlers
    # ------------------------------------------------------------------
    def clear_form(self):
        """Clearing the staff information fields and every currently entered item."""
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, get_today_string())
        self.staff_id_entry.delete(0, tk.END)
        self.staff_name_entry.delete(0, tk.END)
        self.item_name_entry.delete(0, tk.END)
        self.item_cost_entry.delete(0, tk.END)
        self.clear_items()

    def reset_all(self):
        """Confirming with the user, then resetting the form back to a blank state."""
        if messagebox.askyesno(
            "Confirm Reset",
            "Clear the current form? Requisitions already submitted will be kept.",
        ):
            self.clear_form()
            self.refresh_all()

    def exit_app(self):
        """Confirming with the user before closing the application."""
        if messagebox.askyesno("Confirm Exit", "Are you sure you want to exit the application?"):
            self.root.destroy()

    # ------------------------------------------------------------------
    # Global refresh
    # ------------------------------------------------------------------
    def refresh_all(self):
        """Refreshing every data-driven section of the interface in one call."""
        self.refresh_manager_list()
        self.refresh_statistics()
        self.refresh_history()