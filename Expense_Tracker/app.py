from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import csv
import os
from datetime import datetime, timedelta
from collections import defaultdict
import json
import re
import hashlib
import secrets

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# File paths
CSV_FILE = 'expenses.csv'
USERS_FILE = 'users.txt'

# Password validation regex
PASSWORD_PATTERN = r'^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
USERNAME_PATTERN = r'^[a-zA-Z0-9]{6,}$'


def hash_password(password, salt=None):
    """Hash password with unique salt per user"""
    if salt is None:
        # Generate a new random salt for new passwords
        salt = secrets.token_hex(32)  # 64-character hex string

    # Combine password and salt, then hash
    password_salt = password + salt
    hashed = hashlib.sha256(password_salt.encode()).hexdigest()

    return hashed, salt


def init_files():
    """Initialize CSV and users files if they don't exist"""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            # Updated to include date field
            writer.writerow(['id', 'category', 'amount', 'description', 'date', 'username'])

    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as file:
            pass  # Create empty file


def validate_username(username):
    """Validate username format and uniqueness"""
    if not re.match(USERNAME_PATTERN, username):
        return False, "Username must be at least 6 characters long and contain only alphanumeric characters"

    if username_exists(username):
        return False, "Username already exists"

    return True, ""


def validate_password(password):
    """Validate password format"""
    if not re.match(PASSWORD_PATTERN, password):
        return False, "Password must be at least 8 characters long with at least one uppercase letter, one number, and one special character"
    return True, ""


def username_exists(username):
    """Check if username already exists"""
    if not os.path.exists(USERS_FILE):
        return False

    with open(USERS_FILE, 'r') as file:
        for line in file:
            if line.strip():
                stored_username = line.split(':')[0]
                if stored_username == username:
                    return True
    return False


def save_user(username, password):
    """Save user credentials to file with unique salt"""
    hashed_password, salt = hash_password(password)
    with open(USERS_FILE, 'a') as file:
        file.write(f"{username}:{hashed_password}:{salt}\n")


def authenticate_user(username, password):
    """Authenticate user credentials using stored salt"""
    if not os.path.exists(USERS_FILE):
        return False

    with open(USERS_FILE, 'r') as file:
        for line in file:
            if line.strip():
                parts = line.strip().split(':', 2)
                if len(parts) == 3:  # username:hash:salt
                    stored_username, stored_hash, stored_salt = parts
                    if stored_username == username:
                        # Hash the provided password with the stored salt
                        hashed_password, _ = hash_password(password, stored_salt)
                        return hashed_password == stored_hash
                elif len(parts) == 2:  # Handle old format (username:hash) - migration needed
                    stored_username, stored_hash = parts
                    if stored_username == username:
                        # For backward compatibility, use old method
                        old_salt = "expense_tracker_salt"
                        old_hash = hashlib.sha256((password + old_salt).encode()).hexdigest()
                        if old_hash == stored_hash:
                            # Migrate to new format
                            migrate_user_password(username, password)
                            return True
    return False


def migrate_user_password(username, password):
    """Migrate user from old password format to new format"""
    if not os.path.exists(USERS_FILE):
        return

    # Read all users
    users = []
    with open(USERS_FILE, 'r') as file:
        for line in file:
            if line.strip():
                users.append(line.strip())

    # Update the specific user
    updated_users = []
    for user_line in users:
        parts = user_line.split(':', 2)
        if len(parts) >= 2 and parts[0] == username:
            # Generate new hash with unique salt
            new_hash, new_salt = hash_password(password)
            updated_users.append(f"{username}:{new_hash}:{new_salt}")
        else:
            updated_users.append(user_line)

    # Write back to file
    with open(USERS_FILE, 'w') as file:
        for user_line in updated_users:
            file.write(user_line + '\n')


def login_required(f):
    """Decorator to require login for protected routes"""

    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    decorated_function.__name__ = f.__name__
    return decorated_function


def get_next_id():
    """Get the next available ID"""
    try:
        with open(CSV_FILE, 'r') as file:
            reader = csv.DictReader(file)
            ids = [int(row['id']) for row in reader if row['id'].isdigit()]
            return max(ids) + 1 if ids else 1
    except:
        return 1

def get_all_categories():
    """Get all unique categories from expenses."""
    categories = set()
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row.get('category'):
                    categories.add(row['category'])
    return sorted(list(categories))

def read_expenses():
    """Read all expenses from CSV for current user"""
    expenses = []
    current_user = session.get('username')
    if not current_user or not os.path.exists(CSV_FILE):
        return expenses

    with open(CSV_FILE, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['id'] and row.get('username') == current_user:
                # Handle missing date field for backward compatibility
                expense_date = row.get('date', datetime.now().strftime('%Y-%m-%d'))
                expenses.append({
                    'id': int(row['id']),
                    'category': row['category'],
                    'amount': float(row['amount']),
                    'description': row.get('description', ''),
                    'date': expense_date,
                    'username': row.get('username', '')
                })

    # Sort by date (newest first)
    expenses.sort(key=lambda x: x['date'], reverse=True)
    return expenses


def write_expenses(expenses):
    """Write expenses to CSV"""
    with open(CSV_FILE, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['id', 'category', 'amount', 'description', 'date', 'username'])
        writer.writeheader()
        for expense in expenses:
            writer.writerow(expense)


def add_expense(category, amount, description='', date=None):
    """Add a new expense for current user"""
    # Read all expenses (not just current user's)
    all_expenses = []
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['id']:  # Skip empty rows
                    # Handle missing date field for backward compatibility
                    expense_date = row.get('date', datetime.now().strftime('%Y-%m-%d'))
                    all_expenses.append({
                        'id': int(row['id']),
                        'category': row['category'],
                        'amount': float(row['amount']),
                        'description': row.get('description', ''),
                        'date': expense_date,
                        'username': row.get('username', '')
                    })

    # Use provided date or current date
    if not date:
        date = datetime.now().strftime('%Y-%m-%d')

    new_expense = {
        'id': get_next_id(),
        'category': category,
        'amount': float(amount),
        'description': description,
        'date': date,
        'username': session.get('username')
    }
    all_expenses.append(new_expense)
    write_expenses(all_expenses)
    return new_expense


def update_expense(expense_id, category, amount, description='', date=None):
    """Update an existing expense for current user"""
    all_expenses = []
    current_user = session.get('username')

    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['id']:  # Skip empty rows
                    # Handle missing date field for backward compatibility
                    expense_date = row.get('date', datetime.now().strftime('%Y-%m-%d'))
                    all_expenses.append({
                        'id': int(row['id']),
                        'category': row['category'],
                        'amount': float(row['amount']),
                        'description': row.get('description', ''),
                        'date': expense_date,
                        'username': row.get('username', '')
                    })

    for expense in all_expenses:
        if expense['id'] == int(expense_id) and expense['username'] == current_user:
            expense['category'] = category
            expense['amount'] = float(amount)
            expense['description'] = description
            if date:
                expense['date'] = date
            break

    write_expenses(all_expenses)


def delete_expense(expense_id):
    """Delete an expense for current user"""
    all_expenses = []
    current_user = session.get('username')

    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['id']:  # Skip empty rows
                    # Handle missing date field for backward compatibility
                    expense_date = row.get('date', datetime.now().strftime('%Y-%m-%d'))
                    all_expenses.append({
                        'id': int(row['id']),
                        'category': row['category'],
                        'amount': float(row['amount']),
                        'description': row.get('description', ''),
                        'date': expense_date,
                        'username': row.get('username', '')
                    })

    # Remove only the current user's expense
    all_expenses = [expense for expense in all_expenses
                    if not (expense['id'] == int(expense_id) and expense['username'] == current_user)]
    write_expenses(all_expenses)


def get_analysis_data():
    """Get analysis data for dashboard for current user"""
    expenses = read_expenses()

    if not expenses:
        return {
            'total_expense': 0,
            'category_totals': {},
            'highest_category': None,
            'lowest_category': None,
            'all_categories_same': False
        }

    # Total expense (sum of all amounts across all dates)
    total_expense = sum(expense['amount'] for expense in expenses)

    # Total by category (across all dates)
    category_totals = defaultdict(float)
    for expense in expenses:
        category_totals[expense['category']] += expense['amount']

    category_totals = dict(category_totals)

    # Check if all categories have the same total
    if len(set(category_totals.values())) == 1 and len(category_totals) > 1:
        # All categories have the same amount
        amount = list(category_totals.values())[0]
        return {
            'total_expense': total_expense,
            'category_totals': category_totals,
            'highest_category': None,
            'lowest_category': None,
            'all_categories_same': True,
            'same_amount': amount
        }

    # Find highest and lowest spending categories (across all dates)
    if category_totals:
        max_amount = max(category_totals.values())
        min_amount = min(category_totals.values())

        # Find all categories with max amount
        highest_categories = [cat for cat, amount in category_totals.items() if amount == max_amount]

        # Find all categories with min amount
        lowest_categories = [cat for cat, amount in category_totals.items() if amount == min_amount]

        highest_category = {
            'categories': highest_categories,
            'amount': max_amount,
            'is_multiple': len(highest_categories) > 1
        }

        lowest_category = {
            'categories': lowest_categories,
            'amount': min_amount,
            'is_multiple': len(lowest_categories) > 1
        }
    else:
        highest_category = lowest_category = None

    return {
        'total_expense': total_expense,
        'category_totals': category_totals,
        'highest_category': highest_category,
        'lowest_category': lowest_category,
        'all_categories_same': False
    }


def get_trend_analysis_data(start_date_str, end_date_str, category_filter):
    """Get trend analysis data for a given date range and category."""
    expenses = read_expenses() # This reads expenses for the current user

    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

    daily_totals = defaultdict(float)
    filtered_expenses = []

    # Filter expenses by date and category
    for expense in expenses:
        expense_date = datetime.strptime(expense['date'], '%Y-%m-%d').date()
        if start_date <= expense_date <= end_date:
            if category_filter == 'All Categories' or expense['category'] == category_filter:
                daily_totals[expense_date.strftime('%Y-%m-%d')] += expense['amount']
                filtered_expenses.append(expense)


    # Generate labels (dates) for the chart
    delta = end_date - start_date
    dates = []
    for i in range(delta.days + 1):
        day = start_date + timedelta(days=i)
        dates.append(day.strftime('%Y-%m-%d'))

    # Prepare data for the chart, ensuring all dates in range are present
    chart_data = [daily_totals[date] for date in dates]

    # Sort filtered expenses by date for the table
    filtered_expenses.sort(key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d'), reverse=True)

    return {
        'labels': dates,
        'data': chart_data,
        'filtered_expenses': filtered_expenses
    }



# Routes
@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        if authenticate_user(username, password):
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'error')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Validate username
        username_valid, username_error = validate_username(username)
        if not username_valid:
            flash(username_error, 'error')
            return render_template('login.html', show_register=True)

        # Validate password
        password_valid, password_error = validate_password(password)
        if not password_valid:
            flash(password_error, 'error')
            return render_template('login.html', show_register=True)

        # Check password confirmation
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return render_template('login.html', show_register=True)

        # Save user
        try:
            save_user(username, password)
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash('Registration failed. Username might already exist.', 'error')
            return render_template('login.html', show_register=True)

    return render_template('login.html', show_register=True)


@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out successfully!', 'success')
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('index.html', active_tab='add', current_user=session['username'])


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        category = request.form['category']
        amount = request.form['amount']
        description = request.form.get('description', '')
        date = request.form.get('date', '')

        # Validate description length
        if len(description) > 100:
            flash('Description must be 100 characters or less!', 'error')
            return redirect(url_for('add'))

        # Validate date format if provided
        if date:
            try:
                datetime.strptime(date, '%Y-%m-%d')
            except ValueError:
                flash('Invalid date format!', 'error')
                return redirect(url_for('add'))

        try:
            add_expense(category, amount, description, date)
            flash('Expense added successfully!', 'success')
        except Exception as e:
            flash(f'Error adding expense: {str(e)}', 'error')

        return redirect(url_for('add'))

    return render_template('index.html', active_tab='add', current_user=session['username'])


@app.route('/view')
@login_required
def view():
    expenses = read_expenses()
    return render_template('index.html', active_tab='view', expenses=expenses, current_user=session['username'])


@app.route('/edit/<int:expense_id>')
@login_required
def edit(expense_id):
    expenses = read_expenses()
    expense = next((exp for exp in expenses if exp['id'] == expense_id), None)
    if not expense:
        flash('Expense not found!', 'error')
        return redirect(url_for('view'))

    return render_template('index.html', active_tab='edit', expense=expense, expenses=read_expenses(),
                           current_user=session['username'])


@app.route('/update/<int:expense_id>', methods=['POST'])
@login_required
def update(expense_id):
    category = request.form['category']
    amount = request.form['amount']
    description = request.form.get('description', '')
    date = request.form.get('date', '')

    # Validate description length
    if len(description) > 100:
        flash('Description must be 100 characters or less!', 'error')
        return redirect(url_for('edit', expense_id=expense_id))

    # Validate date format if provided
    if date:
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            flash('Invalid date format!', 'error')
            return redirect(url_for('edit', expense_id=expense_id))

    try:
        update_expense(expense_id, category, amount, description, date)
        flash('Expense updated successfully!', 'success')
    except Exception as e:
        flash(f'Error updating expense: {str(e)}', 'error')

    return redirect(url_for('view'))


@app.route('/delete/<int:expense_id>')
@login_required
def delete(expense_id):
    try:
        delete_expense(expense_id)
        flash('Expense deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting expense: {str(e)}', 'error')

    return redirect(url_for('view'))


@app.route('/analysis')
@login_required
def analysis():
    analysis_data = get_analysis_data()
    # Get all unique categories for the filter dropdown
    all_expenses = read_expenses()
    categories = sorted(list(set(e['category'] for e in all_expenses)))
    categories.insert(0, 'All Categories') # Add 'All Categories' option
    sorted_category_totals = sorted(
        analysis_data['category_totals'].items(),
        key=lambda x: x[1],
        reverse=True)
    return render_template('index.html', active_tab='analysis', analysis=analysis_data,
                           current_user=session['username'], categories=categories,sorted_category_totals=sorted_category_totals)


@app.route('/api/trend_analysis')
@login_required
def api_trend_analysis():
    """API endpoint for trend analysis data."""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    category = request.args.get('category')

    if not start_date or not end_date or not category:
        return jsonify({'error': 'Missing start_date, end_date, or category parameter'}), 400

    trend_data = get_trend_analysis_data(start_date, end_date, category)
    return jsonify(trend_data)



if __name__ == '__main__':
    init_files()
    app.run(debug=True)
