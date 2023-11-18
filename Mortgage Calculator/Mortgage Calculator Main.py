import csv
import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter.filedialog import asksaveasfilename

## Created by Ian C Simpson 11-17-23

class MortgageCalculator:
    
    def __init__(self, master):
        self.master = master
        self.master.title("Mortgage Calculator")
        self.master.geometry("400x600")  # Set size of the window
        self.master.minsize(400, 600)    # Set the minimum size of the window

        self.create_widgets()
        self.create_refinance_section()
        
    def create_widgets(self):
        """Create the widgets for the mortgage calculator."""
        entry_frame = tk.Frame(self.master, padx=5, pady=5)
        entry_frame.pack(fill=tk.X)
        
        self.principal_entry = self.create_label_and_entry(entry_frame, "Loan Principal:")
        self.interest_rate_entry = self.create_label_and_entry(entry_frame, "Interest Rate (%):")
        self.num_years_entry = self.create_label_and_entry(entry_frame, "Number of Years:")
        self.property_tax_entry = self.create_label_and_entry(entry_frame, "Annual Property Tax:")
        self.home_insurance_entry = self.create_label_and_entry(entry_frame, "Annual Home Insurance:")
        
        self.interest_only_var = tk.BooleanVar()
        interest_only_checkbox = tk.Checkbutton(entry_frame, text="Interest Only", variable=self.interest_only_var)
        interest_only_checkbox.grid(row=5, columnspan=2, sticky='w')

        calculate_button = tk.Button(entry_frame, text="Calculate Mortgage", command=self.calculate_mortgage)
        calculate_button.grid(row=6, columnspan=2, pady=10, sticky = 'w')

        self.refinance_var = tk.BooleanVar()
        self.refinance_checkbox = tk.Checkbutton(entry_frame, text="Refinance", variable=self.refinance_var, command=self.toggle_refinance)
        self.refinance_checkbox.grid(row=8, columnspan=2, sticky='w')

        self.mortgage_result_label = tk.Label(entry_frame, text="")
        self.mortgage_result_label.grid(row=7, columnspan=2, pady=10)

    def create_label_and_entry(self, parent, text):
        """Create a label and entry widget inside the given parent."""
        label = tk.Label(parent, text=text)
        label.grid(sticky='w')
        entry = tk.Entry(parent)
        entry.grid(row=label.grid_info()['row'], column=1, pady=5, sticky='ew')
        return entry

    def create_refinance_section(self):
        """Create the refinance section of the GUI."""
        self.refinance_frame = tk.LabelFrame(self.master, text="Refinance Options", padx=5, pady=5)
        self.refinance_frame.pack(fill=tk.X, padx=10, pady=5)

        self.refinance_balance_entry = self.create_label_and_entry(self.refinance_frame, "Refinance Balance:")
        self.refinance_interest_rate_entry = self.create_label_and_entry(self.refinance_frame, "Refinance Interest Rate (%):")
        self.refinance_num_years_entry = self.create_label_and_entry(self.refinance_frame, "Refinance Number of Years:")

        self.toggle_refinance()

    def calculate_mortgage(self):
        # Calculate the mortgage and create an amortization chart
        principal = float(self.principal_entry.get())
        interest_rate = float(self.interest_rate_entry.get()) / 100
        num_years = int(self.num_years_entry.get())
        property_tax = float(self.property_tax_entry.get()) / 12  # Annual to monthly
        home_insurance = float(self.home_insurance_entry.get()) / 12  # Annual to monthly

        monthly_payment, amortization_schedule = self.compute_payments(principal, interest_rate, num_years, self.interest_only_var.get())
        
        self.mortgage_result_label.config(text=f"Monthly Payment: ${monthly_payment:.2f}")
        total_monthly_payment = monthly_payment + property_tax + home_insurance

        if self.refinance_var.get():
            refinance_info = self.calculate_refinance(principal, interest_rate, num_years, monthly_payment)
            self.mortgage_result_label.config(text=f"{self.mortgage_result_label.cget('text')}\n{refinance_info}")

        # Display total cost and interest
        total_interest_paid = sum(interest_payment for _, _, interest_payment, _ in amortization_schedule)
        total_paid = principal + total_interest_paid
        self.mortgage_result_label.config(text=(f"Monthly Payment (Principal and Interest): ${monthly_payment:.2f}\n"
                                                f"Monthly Property Tax: ${property_tax:.2f}\n"
                                                f"Monthly Home Insurance: ${home_insurance:.2f}\n"
                                                f"Total Monthly Payment: ${total_monthly_payment:.2f}"))
        
        self.plot_amortization_schedule(amortization_schedule)

    def compute_payments(self, principal, interest_rate, num_years, interest_only):    #interest_only
        """Compute the mortgage payments."""
        monthly_interest_rate = interest_rate / 12
        num_payments = num_years * 12

        if interest_only:
            monthly_payment = principal * monthly_interest_rate
        else:
            monthly_payment = principal * (monthly_interest_rate * (1 + monthly_interest_rate) ** num_payments) / ((1 + monthly_interest_rate) ** num_payments - 1)
        
        amortization_schedule = self.create_amortization_schedule(principal, monthly_interest_rate, num_payments, monthly_payment)
        
        return monthly_payment, amortization_schedule

    def create_amortization_schedule(self, principal, monthly_interest_rate, num_payments, monthly_payment):
        """Create an amortization schedule."""
        remaining_balance = principal
        amortization_schedule = []

        for month in range(1, num_payments + 1):
            interest_payment = remaining_balance * monthly_interest_rate
            principal_payment = monthly_payment - interest_payment
            remaining_balance -= principal_payment

            amortization_schedule.append((month, remaining_balance, interest_payment, principal_payment))

        return amortization_schedule

    def calculate_refinance(self, principal, interest_rate, num_years, current_monthly_payment):
        """Calculate the refinance information."""
        refinance_balance = float(self.refinance_balance_entry.get())
        refinance_interest_rate = float(self.refinance_interest_rate_entry.get()) / 100
        refinance_num_years = int(self.refinance_num_years_entry.get())

        refinance_monthly_payment, _ = self.compute_payments(refinance_balance, refinance_interest_rate, refinance_num_years, False)
        interest_savings = (current_monthly_payment - refinance_monthly_payment) * num_years * 12

        return f"Interest Savings: ${interest_savings:.2f} (if refinanced)"

    def plot_amortization_schedule(self, amortization_schedule):
        """Plot the amortization schedule with an option to save as an image file."""
        months, balances, interest_payments, principal_payments = zip(*amortization_schedule)

        fig, ax1 = plt.subplots(figsize=(10, 6))

        # Plot remaining balance over time
        color = 'tab:blue'
        ax1.set_xlabel('Month')
        ax1.set_ylabel('Remaining Balance', color=color)
        ax1.plot(months, balances, color=color)
        ax1.tick_params(axis='y', labelcolor=color)

        # Twin axis plots the intrest/principal payments 
        ax2 = ax1.twinx()
        color = 'tab:red'
        ax2.set_ylabel('Payment Amount', color=color)
        ax2.plot(months, interest_payments, color=color, linestyle='dotted', label='Interest Payment')
        ax2.plot(months, principal_payments, color='tab:green', linestyle='-', label='Principal Payment')
        ax2.tick_params(axis='y', labelcolor=color)

        # Adds legend
        lines, labels = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines + lines2, labels + labels2, loc='upper right')

        # T & G
        plt.title('Amortization Schedule')
        ax1.grid(True)

        # Save Button
        save_button = plt.Button(plt.axes([0.8, 0.01, 0.1, 0.075]), 'Save Image')
        save_button.on_clicked(lambda event: self.save_plot_as_image(fig))

        plt.show()

    def save_plot_as_image(self, fig):
        """Save the current plot as an image file."""
        filetypes = (
            ('PNG files', '*.png'),
            ('JPEG files', '*.jpg;*.jpeg'),
            ('All files', '*.*')
        )
        filename = asksaveasfilename(
            title='Save as image',
            filetypes=filetypes,
            defaultextension=filetypes
        )
        if filename:
            fig.savefig(filename)
            messagebox.showinfo("Mortgage Calculator", f"Plot saved as {filename}")

    def save_amortization_schedule(self, amortization_schedule):
        """Save the amortization schedule to a CSV file."""
        filename = asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Save Amortization Schedule"
        )

        if not filename:  # If the user cancels the save operation
            return

        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Month", "Remaining Balance", "Interest Payment", "Principal Payment"])
            writer.writerows(amortization_schedule)

        messagebox.showinfo("Mortgage Calculator", "Amortization Schedule saved successfully.")

    def toggle_refinance(self):
        """Toggle the state of the refinance entries."""
        state = tk.NORMAL if self.refinance_var.get() else tk.DISABLED
        self.refinance_balance_entry.config(state=state)
        self.refinance_interest_rate_entry.config(state=state)
        self.refinance_num_years_entry.config(state=state)

if __name__ == "__main__":
    root = tk.Tk()
    app = MortgageCalculator(root)
    root.mainloop()