import tkinter as tk
from tkinter import messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sqlite3
from datetime import datetime


class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")

        # Set the initial size of the window
        self.root.geometry("500x450")

        # Set the background color of the window
        self.root.configure(bg="light blue")

        # Variables
        self.expense_name_var = tk.StringVar()
        self.expense_amount_var = tk.StringVar()
        self.expense_date_var = tk.StringVar()
        self.expense_limit_var = tk.StringVar()

        # Font settings
        font_style = ("Helvetica", 12)

        # GUI Elements
        self.expense_name_label = tk.Label(root, text="Expense Name:", font=font_style, bg="light blue")
        self.expense_name_entry = tk.Entry(root, textvariable=self.expense_name_var, font=font_style)

        self.expense_amount_label = tk.Label(root, text="Expense Amount:", font=font_style, bg="light blue")
        self.expense_amount_entry = tk.Entry(root, textvariable=self.expense_amount_var, font=font_style)

        self.expense_date_label = tk.Label(root, text="Expense Date (YYYY-MM-DD):", font=font_style, bg="light blue")
        self.expense_date_entry = tk.Entry(root, textvariable=self.expense_date_var, font=font_style)

        self.add_expense_button = tk.Button(root, text="Add Expense", command=self.add_expense, font=font_style)
        self.show_expenses_button = tk.Button(root, text="Show Expenses", command=self.show_expenses, font=font_style)

        self.set_limit_label = tk.Label(root, text="Set Monthly Limit (₹):", font=font_style, bg="light blue")
        self.set_limit_entry = tk.Entry(root, textvariable=self.expense_limit_var, font=font_style)
        self.set_limit_button = tk.Button(root, text="Set Limit", command=self.set_expense_limit, font=font_style)

        self.check_limit_button = tk.Button(root, text="Check Limit", command=self.check_limit, font=font_style)

        # Grid layout
        self.expense_name_label.grid(row=0, column=0, padx=10, pady=10)
        self.expense_name_entry.grid(row=0, column=1, padx=10, pady=10)
        self.expense_amount_label.grid(row=1, column=0, padx=10, pady=10)
        self.expense_amount_entry.grid(row=1, column=1, padx=10, pady=10)
        self.expense_date_label.grid(row=2, column=0, padx=10, pady=10)
        self.expense_date_entry.grid(row=2, column=1, padx=10, pady=10)
        self.add_expense_button.grid(row=3, column=0, columnspan=2, pady=10)
        self.show_expenses_button.grid(row=4, column=0, columnspan=2, pady=10)
        self.set_limit_label.grid(row=5, column=0, padx=10, pady=10)
        self.set_limit_entry.grid(row=5, column=1, padx=10, pady=10)
        self.set_limit_button.grid(row=6, column=0, columnspan=2, pady=10)
        self.check_limit_button.grid(row=7, column=0, columnspan=2, pady=10)

        # Connect to the SQLite database
        self.connect_to_database()

    def connect_to_database(self):
        try:
            # Connect to SQLite database
            self.conn = sqlite3.connect('expenses.db')
            self.cursor = self.conn.cursor()

            # Only create table if it doesn't exist
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS expenses
                               (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                name TEXT, 
                                amount REAL, 
                                date TEXT)''')

            # Ensure settings table exists
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS settings
                                   (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                    expense_limit REAL)''')
            self.conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred while setting up the database: {e}")

    def add_expense(self):
        expense_name = self.expense_name_var.get()
        expense_amount = self.expense_amount_var.get()
        expense_date = self.expense_date_var.get() or datetime.now().strftime('%Y-%m-%d')

        if expense_name and expense_amount:
            try:
                expense_amount = float(expense_amount)

                # Validate date format
                try:
                    datetime.strptime(expense_date, '%Y-%m-%d')
                except ValueError:
                    messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD.")
                    return

                # Add the expense to the database
                self.cursor.execute("INSERT INTO expenses (name, amount, date) VALUES (?, ?, ?)",
                                    (expense_name, expense_amount, expense_date))
                self.conn.commit()

                messagebox.showinfo("Expense Added", f"Expense '{expense_name}' added successfully!")
                self.clear_entries()
            except ValueError:
                messagebox.showerror("Error", "Invalid expense amount. Please enter valid value.")
        else:
            messagebox.showerror("Error", "Please enter expense name and amount.")

    def show_expenses(self):
        # Fetch expenses from the database
        self.cursor.execute("SELECT name, amount, date FROM expenses ORDER BY date ASC")
        expenses = self.cursor.fetchall()

        if not expenses:
            messagebox.showinfo("No Expenses", "No expenses to display.")
        else:
            # Extract expense names, amounts, and dates for plotting
            expense_names = [expense[0] for expense in expenses]
            expense_amounts = [expense[1] for expense in expenses]
            expense_dates = [expense[2] for expense in expenses]

            # Combine date and expense name for the x-axis labels
            x_labels = [f"{date}\n{expense_name}" for date, expense_name in zip(expense_dates, expense_names)]

            # Plotting
            fig, ax = plt.subplots()
            ax.bar(x_labels, expense_amounts, color='blue')
            ax.set_ylabel('Expense Amount (₹)')
            ax.set_title('Expense Chart')

            # Rotate the x-axis labels to avoid overlap and make them more readable
            plt.xticks(rotation=45, ha='right')

            # Embed the plot in Tkinter window
            chart_window = tk.Toplevel(self.root)
            chart_window.title("Expense Chart")

            chart_canvas = FigureCanvasTkAgg(fig, master=chart_window)
            chart_canvas.draw()
            chart_canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)

    def set_expense_limit(self):
        try:
            expense_limit = float(self.expense_limit_var.get())
            self.cursor.execute("DELETE FROM settings")  # Ensure only one limit is stored
            self.cursor.execute("INSERT INTO settings (expense_limit) VALUES (?)", (expense_limit,))
            self.conn.commit()
            messagebox.showinfo("Limit Set", f"Monthly limit set to ₹{expense_limit:.2f}")
        except ValueError:
            messagebox.showerror("Error", "Invalid limit amount. Please enter a valid number.")

    def check_limit(self):
        # Calculate total expenses for the current month
        current_month = datetime.now().strftime('%Y-%m')
        self.cursor.execute("SELECT SUM(amount) FROM expenses WHERE date LIKE ?", (f'{current_month}%',))
        total_expenses = self.cursor.fetchone()[0] or 0.0

        # Fetch the limit
        self.cursor.execute("SELECT expense_limit FROM settings")
        limit_row = self.cursor.fetchone()

        if limit_row:
            expense_limit = limit_row[0]
            if total_expenses > expense_limit:
                messagebox.showwarning("Limit Exceeded",
                                       f"Total expenses this month: ₹{total_expenses:.2f}\n"
                                       f"Limit: ₹{expense_limit:.2f}\nYou have exceeded your limit!")
            else:
                messagebox.showinfo("Within Limit",
                                    f"Total expenses this month: ₹{total_expenses:.2f}\n"
                                    f"Limit: ₹{expense_limit:.2f}")
        else:
            messagebox.showinfo("No Limit Set", "Please set a monthly limit first.")

    def clear_entries(self):
        self.expense_name_entry.delete(0, tk.END)
        self.expense_amount_entry.delete(0, tk.END)
        self.expense_date_entry.delete(0, tk.END)

    def __del__(self):
        # Close the database connection when the object is destroyed
        self.conn.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()