import re

app_path = r'c:\Users\Administrator\capstone\MomCare-App-by-MomTech-1\app.py'
with open(app_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Define the whole dashboard function body with correct indentation
new_dashboard_func = """@app.route('/dashboard')
def dashboard():
   first = session.get('user_first')
   today = datetime.now().strftime('%B %d, %Y')
   user_email = session.get('user_email')
   
   tasks = []
   income = 0
   budget_limit = 0
   total_spent_today = 0
   total_spent_month = 0
   pending_count = 0
   progress_percentage = 0
   top_expense_category = "None"
   remaining_budget = 0
   
   # Handle month selection
   selected_month_iso = request.args.get('month')
   selected_month = None
   
   if selected_month_iso:
       try:
           # Parse YYYY-MM
           date_obj = datetime.strptime(selected_month_iso, '%Y-%m')
           selected_month = date_obj.strftime('%B %Y')
       except ValueError:
           # Fallback if invalid format
           selected_month_iso = datetime.now().strftime('%Y-%m')
           selected_month = datetime.now().strftime('%B %Y')
   else:
       # Default to current month
       selected_month_iso = datetime.now().strftime('%Y-%m')
       selected_month = datetime.now().strftime('%B %Y')

   if user_email:
       conn = get_db()
       cur = conn.cursor()
       
       # Auto-delete tasks from previous days
       cleanup_old_tasks(user_email)

       # Load TODAY'S tasks only
       today_iso = datetime.now().strftime('%Y-%m-%d')
       cur.execute('SELECT * FROM tasks WHERE user_email = ? AND task_date = ? ORDER BY start_time ASC', (user_email, today_iso))
       rows = cur.fetchall()
       tasks = [dict(r) for r in rows]

       # Calculate Progress & Pending
       total_tasks = len(tasks)
       done_tasks = len([t for t in tasks if t['completed']])
       pending_count = total_tasks - done_tasks
       progress_percentage = int((done_tasks / total_tasks) * 100) if total_tasks > 0 else 0
       
       # Filter tasks for display (Only show pending)
       tasks = [t for t in tasks if not t['completed']]

       # Budget & Expense Logic
       # 1. Get Budget Limit & Income
       cur.execute('SELECT income, budget_limit FROM monthly_budgets WHERE user_email = ? AND month_iso = ?', (user_email, selected_month_iso))
       budget_row = cur.fetchone()
       if budget_row:
           income = budget_row['income']
           budget_limit = budget_row['budget_limit']

       # 2. Get Total Spent Today
       cur.execute('SELECT amount FROM expenses WHERE user_email = ? AND expense_date = ?', (user_email, today_iso))
       total_spent_today = sum(row['amount'] for row in cur.fetchall())
       
       # 3. Get Monthly Totals (Expenses + Groceries)
       cur.execute('SELECT category, amount FROM expenses WHERE user_email = ? AND month_iso = ?', (user_email, selected_month_iso))
       monthly_expenses_rows = cur.fetchall()
       
       cur.execute('SELECT category, estimated_cost FROM grocery_items WHERE user_email = ? AND month_iso = ?', (user_email, selected_month_iso))
       grocery_rows = cur.fetchall()
       
       total_spent_month = sum(row['amount'] for row in monthly_expenses_rows) + \
                           sum(row['estimated_cost'] or 0 for row in grocery_rows)
       
       # Calculate Top Category
       cat_totals = {c: 0 for c in ["Groceries", "Kids/School", "Transport", "Utilities", "Home Mortgage", "Subscription", "Savings", "Others"]}
       for row in monthly_expenses_rows:
           c = row['category']
           if c not in cat_totals: c = "Others"
           cat_totals[c] += row['amount']
       for row in grocery_rows:
           c = row['category'] or "Groceries"
           if c not in cat_totals: c = "Others"
           cat_totals[c] += (row['estimated_cost'] or 0)
           
       if any(v > 0 for v in cat_totals.values()):
           top_cat = max(cat_totals, key=cat_totals.get)
           top_amt = cat_totals[top_cat]
           if top_amt > 0:
               top_expense_category = f"{top_cat} (₱{top_amt:,.2f})"

       # Determine Status Indicator
       budget_color = "green"
       budget_icon = "fa-check-circle"
       if budget_limit > 0:
           pct = (total_spent_month / budget_limit) * 100
           if pct > 100:
               budget_color = "red"
               budget_icon = "fa-exclamation-circle"
           elif pct >= 70:
               budget_color = "orange"
               budget_icon = "fa-exclamation-triangle"
       elif total_spent_month > 0:
           budget_color = "red"
           budget_icon = "fa-exclamation-circle"

       # Calculate remaining budget (Income minus spent)
       remaining_budget = income - total_spent_month
       
       conn.close()

   return render_template('dashboard.html', first=first, today=today, tasks=tasks,
                          progress_percentage=progress_percentage,
                          pending_count=pending_count,
                          income=income,
                          budget_limit=budget_limit, 
                          total_spent_today=total_spent_today,
                          total_spent_month=total_spent_month,
                          remaining_budget=remaining_budget,
                          top_expense_category=top_expense_category,
                          selected_month=selected_month,
                          selected_month_iso=selected_month_iso,
                          budget_color=budget_color,
                          budget_icon=budget_icon)"""

# Regular expression to match the entire dashboard function
pattern = r"@app\.route\('/dashboard'\)\ndef dashboard\(\):.*?\n\n\n\n\n\n\n\n\n\n\n# JSON API endpoints"
# We match until the next section.
# Let's find exactly what's after dashboard.
match = re.search(r"@app\.route\('/dashboard'\)\ndef dashboard\(\):.*?\n(?=@app\.route|# JSON API)", content, re.DOTALL)
if match:
    new_content = content[:match.start()] + new_dashboard_func + "\n\n" + content[match.end():]
    with open(app_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Dashboard function completely replaced and indented")
else:
    print("Could not find dashboard function with regex")
