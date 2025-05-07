'''
This is a simple simulation of a coffee shop business.
'''

import random
from copy import deepcopy

# Constants of customer range
MIN_CUSTOMERS = 20  # Minimum number of customers per day
MAX_CUSTOMERS = 50  # Maximum number of customers per day

# Prices per unit for each ingredient
PRICE_PER_UNIT = {
    "coffee_beans": 2.0,  # Price per unit of coffee beans
    "milk": 1.0,          # Price per unit of milk
    "sugar": 0.5,         # Price per unit of sugar
    "water": 0.2          # Price per unit of water
}

class Employee:
    def __init__(self, name, salary, efficiency):
        # Initialize an employee with name, salary, and efficiency
        self.name = name
        self.salary = salary
        self.efficiency = efficiency

    def work(self):
        # Simulate employee's work efficiency with random fluctuation
        return self.efficiency * random.uniform(0.8, 1.2)

class Customer:
    def __init__(self, preference):
        # Initialize a customer with a drink preference
        self.preference = preference

    def order(self, menu):
        # Randomly select an item from the menu
        return random.choice(menu)

class Log:
    def __init__(self):
        # Initialize a logbook to store daily records
        self.daily_logs = []

    def record(self, day, revenue, expenses, inventory, customers, unserved_customers, sales_log):
        # Record daily operational data
        self.daily_logs.append({
            "day": day,
            "revenue": revenue,
            "expenses": expenses,
            "inventory": deepcopy(inventory),
            "customers": customers,
            "unserved_customers": unserved_customers,
            "sales_log": deepcopy(sales_log)
        })

    def summary(self):
        # Summarize total revenue, expenses, and net profit
        total_revenue = sum(log["revenue"] for log in self.daily_logs)
        total_expenses = sum(log["expenses"] for log in self.daily_logs)
        net_profit = total_revenue - total_expenses
        return total_revenue, total_expenses, net_profit

class Store:
    def __init__(self, name):
        # Initialize the store with a name, balance, inventory, and other attributes
        self.name = name
        self.balance = 500  # Starting balance
        self.inventory = {
            "coffee_beans": 100,  # Initial inventory of coffee beans
            "milk": 100,          # Initial inventory of milk
            "sugar": 100,         # Initial inventory of sugar
            "water": 100          # Initial inventory of water
        }
        self.employees = []  # List of employees
        self.customers_served = 0  # Total customers served
        self.revenue = 0  # Total revenue
        self.expenses = 0  # Total expenses
        self.menu = []  # Menu items
        self.log = Log()  # Log for daily operations
        self.sales_log = {}  # Track sales for each menu item

    def hire_employee(self, name, salary, efficiency):
        # Hire a new employee and add them to the employee list
        employee = Employee(name, salary, efficiency)
        self.employees.append(employee)

    def restock_all_items(self):
        # Restock all items in the inventory to the target level
        max_item_length = max(len(item) for item in self.inventory.keys())  # Calculate alignment for item names
        max_units_length = max(len(f"+{100}") for _ in self.inventory.keys())  # Maximum width for units
        max_cost_length = max(len(f"${int(PRICE_PER_UNIT[item] * 100)}") for item in self.inventory.keys())  # Maximum width for cost

        for item in self.inventory:
            target_inventory = 100  # Target inventory level
            required_amount = max(0, target_inventory - self.inventory[item])
            price_per_unit = PRICE_PER_UNIT[item]  # Get the price per unit for the item
            if required_amount > 0:
                cost = price_per_unit * required_amount
                if self.balance >= cost:
                    # Fully restock if balance is sufficient
                    self.inventory[item] += required_amount
                    self.balance -= cost
                    self.expenses += int(cost)  # Convert expenses to an integer
                    print(f"Restocked {item.capitalize():<{max_item_length}} : +{required_amount:<{max_units_length}} units, Cost: ${int(cost):<{max_cost_length}}")
                else:
                    # Partially restock if balance is insufficient
                    partial_amount = int(self.balance // price_per_unit)
                    if partial_amount > 0:
                        self.inventory[item] += partial_amount
                        partial_cost = partial_amount * price_per_unit
                        self.balance -= partial_cost
                        self.expenses += int(partial_cost)
                        print(f"Partially restocked {item.capitalize():<{max_item_length}} : +{partial_amount:<{max_units_length}} units, Cost: ${int(partial_cost):<{max_cost_length}}")
                    else:
                        # Unable to restock due to insufficient balance
                        print(f"Unable to restock {item.capitalize():<{max_item_length}} : Insufficient balance")

    def add_menu_item(self, name, price, ingredients):
        # Add a new item to the menu
        self.menu.append({
            "name": name,
            "price": price,
            "ingredients": ingredients
        })
        self.sales_log[name] = 0  # Initialize sales log for this item

    def serve_customer(self, customer):
        # Serve a customer if the required ingredients are available
        item = customer.order(self.menu)
        for ing, qty in item["ingredients"].items():
            if self.inventory.get(ing, 0) < qty:
                return False

        # Deduct the required ingredients from the inventory
        for ing, qty in item["ingredients"].items():
            self.inventory[ing] -= qty
        # Update balance, revenue, and customers served
        self.balance += item["price"]
        self.revenue += item["price"]
        self.customers_served += 1
        self.sales_log[item["name"]] += 1  # Record the sale
        return True

    def pay_employees(self):
        # Pay all employees their salaries
        total_salary = sum(emp.salary for emp in self.employees)
        if self.balance >= total_salary:
            # Deduct salaries from balance and add to expenses
            self.balance -= total_salary
            self.expenses += int(total_salary)
        else:
            # Print a warning if balance is insufficient
            print("Insufficient balance to pay employees.")

    def operate_day(self, day):
        # Simulate one day of operations
        print(f"========== Day {day} ==========")
        self.expenses = 0  # Reset daily expenses
        self.sales_log = {item["name"]: 0 for item in self.menu}  # Reset sales log for the day

        self.restock_all_items()  # Restock all items at the start of the day

        daily_revenue = 0
        daily_expenses = 0
        unserved_customers = 0

        # Calculate the number of customers based on employee efficiency
        num_customers = int(random.randint(MIN_CUSTOMERS, MAX_CUSTOMERS) * 
                            (sum(emp.work() for emp in self.employees) / len(self.employees) if self.employees else 0))

        # Serve each customer
        for _ in range(num_customers):
            cust = Customer(preference=random.choice([item["name"] for item in self.menu]))
            before = self.revenue
            if not self.serve_customer(cust):
                unserved_customers += 1
            after = self.revenue
            daily_revenue += after - before

        # Pay employees and record expenses
        self.pay_employees()
        daily_expenses += self.expenses

        # Record the day's operations in the log
        self.log.record(day, daily_revenue, daily_expenses, self.inventory, num_customers, unserved_customers, self.sales_log)

        # Print daily report
        print(f"End of Day {day}:")
        print(f"  Balance: ${self.balance:.2f}")
        print("  Inventory:")

        # Calculate alignment for inventory output
        max_item_length = max(len(item) for item in self.inventory.keys())
        max_amount_length = max(len(str(amount)) for amount in self.inventory.values())

        for item, amount in self.inventory.items():
            print(f"    {item.capitalize():<{max_item_length}} : {amount:>{max_amount_length}} units")

        # Print sales report
        print("  Sales Report:")
        max_item_length = max(len(item) for item in self.sales_log.keys())
        max_sales_length = max(len(str(count)) for count in self.sales_log.values())

        for item, count in self.sales_log.items():
            print(f"    {item:<{max_item_length}} : {count:>{max_sales_length}} sold")

    def report(self):
        # Generate a summary report of the store's performance
        return self.log.summary()

    def show_status(self):
        # Display the current status of the store
        return {
            "balance": self.balance,
            "revenue": self.revenue,
            "expenses": self.expenses,
            "inventory": self.inventory,
            "customers_served": self.customers_served
        }

def main():
    # Initialize the store
    store = Store("William's Cafe")
    store.hire_employee("Alice", 100, 80)
    store.hire_employee("Bob", 120, 85)

    # Add menu items
    store.add_menu_item("Americano", 6, {"coffee_beans": 1, "water": 1})
    store.add_menu_item("Latte", 6, {"coffee_beans": 1, "milk": 1, "water": 1})
    store.add_menu_item("Espresso", 6, {"coffee_beans": 1})
    store.add_menu_item("Cappuccino", 6, {"coffee_beans": 1, "milk": 1, "sugar": 1})

    # Track total ingredient expenses and sales
    ingredient_expenses = {item: 0 for item in PRICE_PER_UNIT.keys()}
    total_sales_log = {item["name"]: 0 for item in store.menu}
    total_employee_salary = 0

    # Simulate 30 days of operations
    for day in range(1, 31):
        print(f"\nDay {day}:")
        
        # Operate the store for the day
        store.operate_day(day)

        # Update ingredient expenses
        for item in PRICE_PER_UNIT.keys():
            ingredient_expenses[item] += int(PRICE_PER_UNIT[item] * max(0, 100 - store.inventory[item]))

        # Update total sales log
        for item, count in store.sales_log.items():
            total_sales_log[item] += count

        # Update total employee salary
        total_employee_salary += sum(emp.salary for emp in store.employees)

        # Check if the store is out of balance
        if store.balance <= 0:
            print("Store is out of balance. Closing early.")
            break

    # Generate final report
    revenue, expenses, profit = store.report()
    print("\n========== Final Report ==========")

    # Align revenue, expenses, and profit
    max_label_length = max(len(label) for label in ["Total Revenue", "Total Expenses", "Net Profit"])
    print(f"{'Total Revenue':<{max_label_length}} : ${revenue}")
    print(f"{'Total Expenses':<{max_label_length}} : ${expenses}")
    print(f"{'Net Profit':<{max_label_length}} : ${profit}")

    # Align ingredient expenses
    print("\n---------- Ingredient Expenses ----------")
    max_item_length = max(len(item) for item in ingredient_expenses.keys())
    for item, cost in ingredient_expenses.items():
        print(f"{item.capitalize():<{max_item_length}} : ${cost}")

    # Align employee salaries
    print("\n---------- Employee Salaries ----------")
    print(f"{'Total Employee Salary':<{max_label_length}} : ${total_employee_salary}")

    # Align total coffee sales
    print("\n---------- Total Coffee Sales ----------")
    max_item_length = max(len(item) for item in total_sales_log.keys())
    for item, count in total_sales_log.items():
        print(f"{item:<{max_item_length}} : {count} sold")

if __name__ == "__main__":
    main()