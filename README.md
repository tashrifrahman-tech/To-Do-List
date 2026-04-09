# ✅ CLI To-Do List

A terminal-based task manager built with **Python** and **MySQL**. Manage your daily tasks with priorities, deadlines, categories, and status tracking — all from the command line with a clean, colorful UI.

---

## Features

- Add tasks with title, category, priority, and due date
- Duplicate task detection — no repeated tasks
- View tasks filtered by priority, status, category, overdue, or due today
- Update any field — title, category, priority, or due date
- Mark tasks as Pending, In Progress, or Done
- Delete tasks with confirmation prompt
- Smart sorting — tasks always ordered High → Medium → Low priority
- Startup reminders for overdue and due-today tasks
- Sequential S.No that always resets after deletions

---

## Requirements

- Python 3.x
- MySQL Server
- Python packages:
  ```
  mysql-connector-python
  tabulate
  rich
  ```

Install dependencies:
```bash
pip install mysql-connector-python tabulate rich
```

---

## Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/cli-todo.git
   cd cli-todo
   ```

2. **Start your MySQL server**

3. **Configure credentials** — open `todo.py` and update if needed:
   ```python
   conn = mysql.connector.connect(
       host="localhost",
       user="root",
       password=""   # add your MySQL password here
   )
   ```

4. **Run the app**
   ```bash
   python todo.py
   ```

The database `todo_db` and `tasks` table are created automatically on first run.

---

## Database Schema

| Column       | Type                                 | Description                   |
|--------------|--------------------------------------|-------------------------------|
| `id`         | INT (PK, AUTO)                       | Internal ID, auto-incremented |
| `title`      | VARCHAR(255)                         | Task title                    |
| `category`   | VARCHAR(100)                         | Task category                 |
| `priority`   | ENUM('High','Medium','Low')          | Task priority level           |
| `status`     | ENUM('Pending','In Progress','Done') | Current task status           |
| `due_date`   | DATE                                 | Optional deadline             |
| `created_at` | DATE                                 | Date the task was created     |

---

## Usage

```
Main Menu:
1. Add Task
2. View Tasks
3. Update Task
4. Delete Task
5. Mark Task Status
6. Exit
```

### Categories
Work · Study · Personal · Health · Finance · Other

### Priorities
High · Medium · Low

### Statuses
Pending · In Progress · Done

---

## View Options

| Option    | Description                                  |
|-----------|----------------------------------------------|
| All Tasks | Every task sorted by priority then due date  |
| By Priority | Filter by High, Medium, or Low             |
| By Status | Filter by Pending, In Progress, or Done      |
| By Category | Filter by a specific category              |
| Overdue   | Tasks past their due date that aren't done   |
| Due Today | Tasks due on today's date that aren't done   |

---

## Project Structure

```
cli-todo/
│
├── todo.py      # Main application
└── README.md    # Project documentation
```

---

## Tech Stack

- **Python** — core logic
- **MySQL** — data persistence
- **Rich** — terminal UI styling and panels
- **Tabulate** — formatted task tables

---

## Author

Made with Python 🐍 and MySQL 🐬
