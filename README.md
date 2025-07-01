# Expense Tracker Flask Application

A simple and secure web-based expense tracking application built with Flask. This application allows users to manage their personal expenses with features like user authentication, expense categorization, and data persistence.
Capgemini NGT Programming Solution Exercises

## 📋 Features

- **Secure User Authentication** - Hash + salt password storage
- **Expense Management** - Add, view, and categorize expenses
- **Data Persistence** - CSV-based storage system
- **Responsive Design** - Clean and intuitive web interface
- **Multiple User Support** - Individual user expense tracking
- **Category Organization** - Organize expenses by categories (Food, Transport, Entertainment, etc.)

## 🏗️ Project Structure

```
Expense_Tracker/
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── expenses.csv             # Expense data storage
├── users.txt               # User credentials (hashed)
├── static/                 # Static assets
│   └── css/
│       ├── index.css       # Dashboard styling
│       └── login.css       # Login page styling
└── templates/              # HTML templates
    ├── login.html          # Login page
    └── index.html          # Main dashboard
```

## 🚀 Installation & Setup

### Step 1: Install Python

**Windows:**
1. Visit [python.org/downloads](https://www.python.org/downloads/)
2. Download and run the latest Python installer
3. ⚠️ **Important**: Check "Add Python to PATH" during installation
4. Verify installation:
   ```cmd
   python --version
   pip --version
   ```

**macOS:**
1. Visit [python.org/downloads](https://www.python.org/downloads/)
2. Download and run the .pkg installer
3. Verify installation:
   ```bash
   python3 --version
   pip3 --version
   ```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3 python3-pip
python3 --version
pip3 --version
```

### Step 2: Download Project
Download and extract the project files to your desired location.

### Step 3: Navigate to Project Directory
```bash
cd Expense_Tracker
```

### Step 4: Install Dependencies
```bash
# Windows
pip install -r requirements.txt

# macOS/Linux
pip3 install -r requirements.txt
```

### Step 5: Run the Application
```bash
# Windows
python app.py

# macOS/Linux
python3 app.py
```

### Step 6: Access the Application
1. Open your web browser
2. Navigate to: `http://localhost:5000`
3. You should see the login page

## 🔑 Credentials

The user can register in the application

## 📸 Screenshots

### Login Page
<!-- Add screenshot here -->
<img src="https://github.com/user-attachments/assets/7ac0a3c3-447b-445c-b52f-da4a82ecdac8" width=75%/></br>

*The secure login interface with user registration option*

### Register Page
<!-- Add screenshot here -->
<img src="https://github.com/user-attachments/assets/caaccb89-51ae-4f88-9e58-8c066edfa185" width=30% height="500"></br>



### Dashboard
<!-- Add screenshot here -->
*Main dashboard showing expense overview and management*
<img src="https://github.com/user-attachments/assets/63747433-efa7-4e57-a2cb-99208001525c" width=75%></br>
![image]()


### Add Expense
<!-- Add screenshot here -->
*Expense entry form with category selection*
<img src="https://github.com/user-attachments/assets/7c4f39d0-54ff-435d-8da4-c2ab1c26eac3" width=75%></br>



## 🧪 Testing the Application

### Authentication Testing
1. **Valid Login**: Create your `testuser` / `password`
2. **Invalid Login**: Try incorrect credentials
3. **Registration**: Create new user account
4. **Logout**: Test logout functionality

### Expense Management Testing
1. **View Expenses**: Check dashboard displays seed data
2. **Add New Expense**: Use the expense form
3. **Data Persistence**: Restart app and verify data remains
4. **Categories**: Test different expense categories

### Data Verification
```bash
# Check expense data
cat expenses.csv

# View user data
head users.txt
```

## 🛠️ Troubleshooting

### Common Issues

**Python Not Found:**
```bash
# Windows: Use full path if needed
C:\Python3x\python.exe app.py

# macOS/Linux: Use python3
python3 app.py
```

**Port Already in Use:**
```bash
# Windows
netstat -ano | findstr :5000

# macOS/Linux
sudo lsof -ti:5000 | xargs kill -9
```

**Dependencies Installation Failed:**
```bash
# Update pip first
pip install --upgrade pip
pip install -r requirements.txt
```

## 📁 Sample Data

The application includes sample data for immediate testing:

**Expense Categories:**
- Food & Dining
- Transportation
- Entertainment
- Utilities
- Healthcare
- Shopping

**Sample Expenses:**
- Restaurant meals, groceries, and transportation costs
- Entertainment expenses, utility bills
- Healthcare and shopping expenses

## 🔒 Security Features

- **Password Hashing**: Secure password storage with salt
- **Session Management**: User session handling
- **Input Validation**: Form data validation
- **Route Protection**: Login required for protected routes


## 📝 Technical Details

**Built With:**
- Flask 2.3.3
- Python 3.x
- HTML5/CSS3
- CSV for data storage

**Key Components:**
- User authentication system
- CRUD operations for expenses
- File-based data persistence
- Responsive web design

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

If you encounter any issues or have questions:
1. Check the troubleshooting section above
2. Verify all installation steps were followed
3. Ensure Python and dependencies are properly installed

---

**Happy Expense Tracking! 💰📊**
