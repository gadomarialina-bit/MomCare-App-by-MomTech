# Database Schema - MomCare App

This document describes the database schema for the MomCare application, stored in `users.db`.

## Tables

### 1. users
Stores user account information and profile details.

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | INTEGER | Primary Key, Autoincrement |
| `first` | TEXT | First Name |
| `last` | TEXT | Last Name |
| `email` | TEXT | Unique Email Address (used as ID) |
| `birthdate` | TEXT | User's Birth Date |
| `password_hash` | TEXT | Hashed Password |
| `security_question` | TEXT | Security Question for Recovery |
| `security_answer` | TEXT | Hashed/Encrypted Security Answer |
| `gender` | TEXT | User's Gender |
| `height` | TEXT | User's Height (cm) |
| `weight` | TEXT | User's Weight (kg) |
| `profile_picture` | TEXT | Path to Profile Picture |

### 2. daily_moods
Tracks user's emotional state on a daily basis.

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | INTEGER | Primary Key, Autoincrement |
| `user_email` | TEXT | Foreign Key (users.email) |
| `date` | TEXT | ISO Date (YYYY-MM-DD) |
| `mood` | TEXT | Mood Label (Happy, Neutral, Tired, Stressed) |
| `mood_score` | INTEGER | Numeric Score (0-3) |
| `created_at` | TEXT | ISO Timestamp |
| **Unique** | `(user_email, date)` | One entry per user per day |

### 3. daily_wellness
Tracks physical wellness metrics on a daily basis.

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | INTEGER | Primary Key, Autoincrement |
| `user_email` | TEXT | Foreign Key (users.email) |
| `date` | TEXT | ISO Date (YYYY-MM-DD) |
| `sleep` | TEXT | Hours of Sleep |
| `water` | TEXT | Glasses of Water |
| `activity` | TEXT | Physical Activity Performed |
| `stress` | INTEGER | Stress Level (1-10) |
| `created_at` | TEXT | ISO Timestamp |
| **Unique** | `(user_email, date)` | One entry per user per day |

### 4. monthly_budgets
Stores budget limits and income per month.

| Column | Type | Description |
| :--- | :--- | :--- |
| `user_email` | TEXT | Foreign Key (users.email) |
| `month_iso` | TEXT | YYYY-MM |
| `income` | REAL | Total Monthly Income |
| `budget_limit` | REAL | Monthly Spending Limit |

### 5. expenses
Tracks individual expenses.

| Column | Type | Description |
| :--- | :--- | :--- |
| `user_email` | TEXT | Foreign Key (users.email) |
| `month_iso` | TEXT | YYYY-MM |
| `category` | TEXT | e.g., Food, Transport |
| `amount` | REAL | Expense Amount |
| `expense_date` | TEXT | Date of Expense |

### 6. tasks
Daily tasks and reminders.

| Column | Type | Description |
| :--- | :--- | :--- |
| `user_email` | TEXT | Foreign Key (users.email) |
| `title` | TEXT | Task Title |
| `task_date` | TEXT | Date for the Task |
| `completed` | INTEGER | 0 or 1 |

### 7. grocery_items
Shopping list items.

| Column | Type | Description |
| :--- | :--- | :--- |
| `user_email` | TEXT | Foreign Key (users.email) |
| `item_name` | TEXT | Name of Item |
| `is_checked` | INTEGER | 0 or 1 |

### 8. reminders & reminder_items
System and user-defined reminders.
