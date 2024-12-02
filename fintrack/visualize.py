from config import get_expenses, get_incomes, get_categorized_expenses
from flask import session
import matplotlib.pyplot as plt
from io import BytesIO
import base64

def rgb_to_css_color(rgb_tuple):
    r, g, b = (int(255 * value) for value in rgb_tuple)  # Scale to 0-255
    return f"rgb({r}, {g}, {b})"

def pie_chart():
    # Fetch categorized expenses
    categorized_expenses = get_categorized_expenses(session['user_id'])  
    # Example: [('Food', 200), ('Transport', 150), ('Rent', 500)]

    # Extract labels and values
    labels = [expense[0] for expense in categorized_expenses]
    values = [expense[1] for expense in categorized_expenses]

    # Generate colors using a Matplotlib color palette
    colors = plt.cm.tab20.colors[:len(labels)]

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(10, 10))  # Adjust figure size as needed

    # Create the donut chart
    wedges, texts, autotexts = ax.pie(
        values, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90,
        wedgeprops={'width': 0.4}  # Donut effect by reducing wedge width
    )
    ax.axis('equal')  # Equal aspect ratio ensures the pie is circular.

    # Generate legend data by converting colors to CSS format
    legend_data = [{'label': label, 'color': rgb_to_css_color(color)} for label, color in zip(labels, colors)]

    # Save chart to BytesIO buffer
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    chart_data = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    
    return chart_data, legend_data

def inc_exp_pie():
    # Generate donut chart
    expenses = get_expenses(session['user_id'])
    incomes = get_incomes(session['user_id'])

    total_expense = sum(expense[3] for expense in expenses)
    total_income = sum(income[3] for income in incomes)

    labels = ['Expenses', 'Incomes']
    values = [total_expense, total_income]
    colors = ['#ff9999', '#66b3ff']  # Customize colors

    # Adjust figure size (smaller dimensions)
    fig, ax = plt.subplots(figsize=(10, 10))  # Example: 4x4 inches

    # Create a donut chart by setting the width of the wedges
    ax.pie(values, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90,
           wedgeprops={'width': 0.4})  # Adjust width for the "donut hole"
    ax.axis('equal')  # Equal aspect ratio ensures the pie is circular.

    # Save plot to BytesIO
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')  # 'bbox_inches' removes extra white space
    buf.seek(0)
    chart_data = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    return chart_data
