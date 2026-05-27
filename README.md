
# Personal Expense Tracker

## Project Type
Full Stack Web Application

## Technologies Used
- Python
- Flask
- MySQL
- HTML
- CSS
- JavaScript

---

# Project Description

Personal Expense Tracker is a web application where users can register, login, and manage their personal expenses securely.

Each user can:
- Add expenses
- Edit expenses
- Delete expenses
- Filter expenses
- View dashboard summary
- View category-wise spending

The project uses session-based authentication so users can only access their own data.

---

# Features

## Authentication
- User Registration
- User Login
- Logout
- Password Hashing using Bcrypt

## Expense Management
- Add Expense
- Edit Expense
- Delete Expense
- View Expenses
- Filter by Category
- Filter by Date

## Dashboard
- Total Expenses
- Total Amount Spent
- Highest Expense
- Category Summary
- Recent Expenses

---

# Database Tables

## Users Table
Stores:
- Username
- Email
- Password

## Expenses Table
Stores:
- Expense Title
- Amount
- Category
- Date
- Note
- User ID

---

# SQL Used

## Category Summary Query

//sql
SELECT category, SUM(amount) AS total
FROM expenses
WHERE user_id = %s
GROUP BY category;


---

# Project Structure

expense-tracker/
│
├── app.py
│
└── static/
├── login.html
├── register.html
├── dashboard.html
├── expenses.html
├── style.css
└── script.js

---

# How to Run the Project

## Install Packages

//bash
pip install flask flask-bcrypt flask-cors mysql-connector-python


## Run MySQL Database

Create database:

sql
CREATE DATABASE expense_tracker;

## Run Flask App

//bash
python app.py

Open in browser:

//text
http://127.0.0.1:5000


---

# Security

* Session-based authentication
* Password hashing
* User-specific data access
* Parameterized SQL queries

---

# Conclusion

This project helped in understanding:

* Flask backend development
* MySQL database connectivity
* User authentication
* CRUD operations
* Session management
* Frontend and backend integration
