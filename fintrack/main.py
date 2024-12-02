from flask import Flask, render_template, request, session, redirect, url_for
from config import get_user_info, insert_new_user, user_exists, add_expense ,get_expenses, add_income, get_incomes, delete_user_expense, delete_user_income
from visualize import pie_chart
from datetime import datetime,timedelta
from matplotlib import rcParams
from matplotlib.dates import DateFormatter
from io import BytesIO
import matplotlib.pyplot as plt
import base64


app = Flask(__name__)
app.secret_key = "padeswori" 


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        results = get_user_info(username, password)
        if results: 
            user_id = results[0]
            email = results[3]
            session['username'] = username
            session['email'] = email
            session['user_id'] = user_id
            return redirect(url_for('home')) 
        else: 
            return render_template('login.html', alert="Invalid username or password.")
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        if not user_exists(username, email): 
            insert_new_user(username, password, email)
            return redirect(url_for('login'))
        else: 
            return render_template('signup.html', alert="User already exists.")
    return render_template('signup.html')

@app.route('/')
def home():
    if 'username' in session: 
        chart_data,legend_data = pie_chart()
       
        expenses = get_expenses(session['user_id'])
        return render_template('home.html', username=session['username'], email = session['email'], chart_data = chart_data, legend_data=legend_data, expenses=expenses )
    else: 
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('email', None)
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/expenses', methods= ['GET','POST'])
def expenses():
    if 'username' in session:
        
        if request.method == "POST":
            date = request.form['date']
            category = request.form['category']
            amount = request.form['amount']
            description = request.form['description']
            add_expense(date, category, amount, description, session['user_id'])
        expenses = get_expenses(session['user_id'])
        chart_data,legend_data = pie_chart()
        return render_template('expenses.html', username=session['username'], email = session['email'], expenses = expenses, chart_data = chart_data ,css_file= "css/expense.css",legend_data= legend_data)
    else: 
        return redirect(url_for('login'))
    
@app.route('/delete_expenses', methods= ['GET','POST'])
def delete_expenses():
    if 'username' in session:
        transaction_id = request.args.get('transaction_id')
        if transaction_id:
            delete_user_expense(transaction_id)
            return redirect(url_for('expenses'))
        else: 
            return "Transaction ID not provided", 400
    else: 
        return redirect(url_for('login'))
    
@app.route('/delete_incomes', methods= ['GET','POST'])
def delete_incomes():
    if 'username' in session:
        transaction_id = request.args.get('transaction_id')
        if transaction_id:
            delete_user_income(transaction_id)
            return redirect(url_for('wallets'))
        else: 
            return "Transaction ID not provided", 400
    else: 
        return redirect(url_for('login'))
    
@app.route('/wallets', methods = ['GET', 'POST'])
def wallets():
    if 'username' in session:
        
        if request.method == "POST":
            date = request.form['date']
            source = request.form['source']
            amount = request.form['amount']
            description = request.form['description']
            add_income(date, source, amount, description, session['user_id'])
        
        incomes = get_incomes(session['user_id'])
        chart_data,legend_data = pie_chart()
        return render_template('wallets.html',incomes = incomes, username=session['username'], email = session['email'], expenses = expenses, chart_data = chart_data, css_file = "css/wallet.css", legend_data=legend_data)
    else: 
        return redirect(url_for('login'))

@app.route('/summary')
def summary():
    if 'username' in session:
        # Fetch expenses and incomes
        expenses = get_expenses(session['user_id'])
        incomes = get_incomes(session['user_id'])

        # Calculate total expenses and income
        total_expense = sum(expense[3] for expense in expenses)
        total_income = sum(income[3] for income in incomes)

        # Prepare data for line graph (expenses over time)
        dates = [expense[1] for expense in expenses]  # Extract dates
        expenses_amount = [expense[3] for expense in expenses]  # Extract expense amounts

        # Convert dates to a readable format
        dates = [str(date) for date in dates]

        fig2, ax2 = plt.subplots(figsize=(10, 5))

        # Plot data
        ax2.plot(dates, expenses_amount, marker='o', linestyle='-', color='b', label='Expenses')

        # Set title and labels
       
        # Clean up x-axis
        ax2.xaxis.set_major_formatter(DateFormatter('%b %d'))  # Format as "Month Day" (e.g., "Nov 20")
        # plt.xticks(rotation=45)  # Rotate x-axis labels
        plt.tight_layout()       # Prevent labels from getting cut off

        # Add grid and legend
        ax2.grid(True)
        ax2.legend()

        # Save line graph as Base64
        buf2 = BytesIO()
        plt.savefig(buf2, format='png', bbox_inches='tight')
        buf2.seek(0)
        line_graph_data = base64.b64encode(buf2.read()).decode('utf-8')
        buf2.close()

        # Prepare data for comparison graph (last month)
        one_month_ago = datetime.now() - timedelta(days=30)
        last_month_expenses = [expense for expense in expenses if expense[1] >= one_month_ago]
        last_month_incomes = [income for income in incomes if income[1] >= one_month_ago]

        last_month_dates = sorted(set(expense[1] for expense in last_month_expenses) | 
                                  set(income[1] for income in last_month_incomes))

        last_month_expense_data = {date: 1 for date in last_month_dates}
        last_month_income_data = {date: 1 for date in last_month_dates}

        for expense in last_month_expenses:
            last_month_expense_data[expense[1]] += expense[3]

        for income in last_month_incomes:
            last_month_income_data[income[1]] += income[3]
       # Generate indices for the bar chart
        x_indices = range(len(last_month_dates))

        # Define the width of the bars
        bar_width = 0.35
        # Generate bar chart for last month's comparison
        fig3, ax3 = plt.subplots(figsize=(10, 5))

        # Plot data
        ax3.bar([x - bar_width/2 for x in x_indices], 
                last_month_expense_data.values(), 
                width=bar_width, label='Expenses', color='red')
        ax3.bar([x + bar_width/2 for x in x_indices], 
                last_month_income_data.values(), 
                width=bar_width, label='Incomes', color='green')

        # Set title and labels
        # ax3.set_title('Comparison of Expenses and Incomes - Last Month')
        # ax3.set_xlabel('Date')
        # ax3.set_ylabel('Amount')

        # Clean up x-axis
                # Clean up x-axis
        ax3.set_xticks(x_indices)
        ax3.set_xticklabels([date.strftime('%b %d') for date in last_month_dates])  # Format as "Month Day"

        # Ensure labels are not italicized
        for label in ax3.get_xticklabels():
            label.set_fontstyle('normal')

        # plt.xticks(rotation=45)  # Rotate labels for readability
        plt.tight_layout()       # Prevent labels from being cut off

        # Add legend
        ax3.legend()
        # Save comparison graph as Base64
        buf3 = BytesIO()
        plt.savefig(buf3, format='png', bbox_inches='tight')
        buf3.seek(0)
        comparison_graph_data = base64.b64encode(buf3.read()).decode('utf-8')
        buf3.close()
        
        chart_data,legend_data = pie_chart()

        # Render template
        return render_template('summary.html',
                               total_expense=total_expense,
                               total_income=total_income,
                               line_graph_data=line_graph_data,
                               comparison_graph_data=comparison_graph_data,
                               username=session['username'], 
                               email = session['email'], 
                               expenses = expenses, 
                               chart_data = chart_data,
                               legend_data = legend_data,
                               css_file= "css/summary.css")
    else:
        return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
