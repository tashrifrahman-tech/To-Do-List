import mysql.connector
from tabulate import tabulate
from rich.console import Console
from rich.panel import Panel
from datetime import datetime, date

# ── Setup ──────────────────────────────────────────────────────────────────────

console = Console()

# ── Database Setup ─────────────────────────────────────────────────────────────

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password=""
)
cursor = conn.cursor()

cursor.execute("CREATE DATABASE IF NOT EXISTS todo_db")
conn.database = "todo_db"

cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    category VARCHAR(100) DEFAULT 'General',
    priority ENUM('High', 'Medium', 'Low') DEFAULT 'Medium',
    status ENUM('Pending', 'In Progress', 'Done') DEFAULT 'Pending',
    due_date DATE,
    created_at DATE NOT NULL
)
""")
conn.commit()


# ── Constants ──────────────────────────────────────────────────────────────────

PRIORITIES = ["High", "Medium", "Low"]
STATUSES   = ["Pending", "In Progress", "Done"]
CATEGORIES = ["Work", "Study", "Personal", "Health", "Finance", "Other"]
HEADERS    = ["S.No", "Title", "Category", "Priority", "Status", "Due Date", "Created"]


# ── Helpers ────────────────────────────────────────────────────────────────────

def number_rows(results):
    return [(i, *row) for i, row in enumerate(results, start=1)]

def pick_from_list(label, options):
    print(f"\n{label}:")
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")
    while True:
        try:
            choice = int(input(f"Choose (1-{len(options)}): ").strip())
            if 1 <= choice <= len(options):
                return options[choice - 1]
            raise ValueError
        except ValueError:
            console.print(f"[red]Enter a number between 1 and {len(options)}.[/red]")

def get_due_date():
    due_input = input("Due date (YYYY-MM-DD, press Enter to skip): ").strip()
    if not due_input:
        return None
    try:
        return datetime.strptime(due_input, "%Y-%m-%d").date()
    except ValueError:
        console.print("[red]Invalid date format. Skipping due date.[/red]")
        return None

def print_tasks(results):
    if not results:
        console.print("[red]No tasks found.[/red]")
        return
    formatted = []
    for row in number_rows(results):
        row = list(row)
        row[6] = row[6] if row[6] else "—"
        formatted.append(row)
    print(tabulate(formatted, headers=HEADERS, tablefmt="grid"))
    console.print(f"[dim]Total: {len(results)} task(s)[/dim]")


# ── Menus ──────────────────────────────────────────────────────────────────────

def display_main_menu():
    console.print(Panel(
        "[bold cyan]CLI To-Do List[/bold cyan]\n\n"
        "[white]1.[/white] Add Task\n"
        "[white]2.[/white] View Tasks\n"
        "[white]3.[/white] Update Task\n"
        "[white]4.[/white] Delete Task\n"
        "[white]5.[/white] Mark Task Status\n"
        "[white]6.[/white] Exit",
        title="Main Menu", border_style="cyan"
    ))

def display_view_menu():
    print("\nView Options:")
    print("1. All Tasks")
    print("2. By Priority")
    print("3. By Status")
    print("4. By Category")
    print("5. Overdue Tasks")
    print("6. Due Today")
    print("7. Go Back")

def display_update_menu():
    print("\nUpdate Options:")
    print("1. Update Title")
    print("2. Update Category")
    print("3. Update Priority")
    print("4. Update Due Date")
    print("5. Go Back")


# ── Add Task ───────────────────────────────────────────────────────────────────

def add_task():
    console.print("\n[bold green]── Add Task ──[/bold green]")

    title = input("Task title: ").strip()
    if not title:
        console.print("[red]Title cannot be empty.[/red]")
        return

    cursor.execute("SELECT COUNT(*) FROM tasks WHERE title = %s AND status != 'Done'", (title,))
    if cursor.fetchone()[0] > 0:
        console.print("[red]A task with this title already exists and is not done yet.[/red]")
        return

    category = pick_from_list("Category", CATEGORIES)
    priority = pick_from_list("Priority", PRIORITIES)
    due_date = get_due_date()

    cursor.execute(
        "INSERT INTO tasks (title, category, priority, status, due_date, created_at) VALUES (%s, %s, %s, 'Pending', %s, %s)",
        (title, category, priority, due_date, date.today())
    )
    conn.commit()
    console.print(f"\n[bold green]✓ Task '{title}' added successfully![/bold green]")


# ── View Tasks ─────────────────────────────────────────────────────────────────

def view_tasks():
    while True:
        display_view_menu()
        choice = input("Choose: ").strip()

        if choice == "1":
            cursor.execute(
                "SELECT title, category, priority, status, due_date, created_at FROM tasks ORDER BY FIELD(priority,'High','Medium','Low'), due_date"
            )
            print_tasks(cursor.fetchall())

        elif choice == "2":
            priority = pick_from_list("Priority", PRIORITIES)
            cursor.execute(
                "SELECT title, category, priority, status, due_date, created_at FROM tasks WHERE priority = %s ORDER BY due_date",
                (priority,)
            )
            print_tasks(cursor.fetchall())

        elif choice == "3":
            status = pick_from_list("Status", STATUSES)
            cursor.execute(
                "SELECT title, category, priority, status, due_date, created_at FROM tasks WHERE status = %s ORDER BY FIELD(priority,'High','Medium','Low')",
                (status,)
            )
            print_tasks(cursor.fetchall())

        elif choice == "4":
            category = pick_from_list("Category", CATEGORIES)
            cursor.execute(
                "SELECT title, category, priority, status, due_date, created_at FROM tasks WHERE category = %s ORDER BY FIELD(priority,'High','Medium','Low')",
                (category,)
            )
            print_tasks(cursor.fetchall())

        elif choice == "5":
            cursor.execute(
                "SELECT title, category, priority, status, due_date, created_at FROM tasks WHERE due_date < %s AND status != 'Done' ORDER BY due_date",
                (date.today(),)
            )
            results = cursor.fetchall()
            if results:
                console.print("\n[bold red]Overdue Tasks[/bold red]")
            print_tasks(results)

        elif choice == "6":
            cursor.execute(
                "SELECT title, category, priority, status, due_date, created_at FROM tasks WHERE due_date = %s AND status != 'Done'",
                (date.today(),)
            )
            results = cursor.fetchall()
            if results:
                console.print("\n[bold yellow]Due Today[/bold yellow]")
            print_tasks(results)

        elif choice == "7":
            break
        else:
            console.print("[red]Invalid option.[/red]")


# ── Update Task ────────────────────────────────────────────────────────────────

def update_task():
    console.print("\n[bold yellow]── Update Task ──[/bold yellow]")

    cursor.execute(
        "SELECT title, category, priority, status, due_date, created_at FROM tasks WHERE status != 'Done' ORDER BY FIELD(priority,'High','Medium','Low')"
    )
    results = cursor.fetchall()
    if not results:
        console.print("[red]No active tasks to update.[/red]")
        return

    print_tasks(results)

    try:
        sno = int(input("\nEnter S.No of task to update: ").strip())
        if sno < 1 or sno > len(results):
            console.print("[red]Invalid S.No.[/red]")
            return
    except ValueError:
        console.print("[red]Invalid input.[/red]")
        return

    task_title = results[sno - 1][0]

    while True:
        display_update_menu()
        choice = input("Choose: ").strip()

        if choice == "1":
            new_title = input("New title: ").strip()
            if not new_title:
                console.print("[red]Title cannot be empty.[/red]")
                continue
            cursor.execute("UPDATE tasks SET title = %s WHERE title = %s", (new_title, task_title))
            conn.commit()
            console.print("[bold green]✓ Title updated.[/bold green]")
            task_title = new_title

        elif choice == "2":
            new_cat = pick_from_list("New Category", CATEGORIES)
            cursor.execute("UPDATE tasks SET category = %s WHERE title = %s", (new_cat, task_title))
            conn.commit()
            console.print("[bold green]✓ Category updated.[/bold green]")

        elif choice == "3":
            new_pri = pick_from_list("New Priority", PRIORITIES)
            cursor.execute("UPDATE tasks SET priority = %s WHERE title = %s", (new_pri, task_title))
            conn.commit()
            console.print("[bold green]✓ Priority updated.[/bold green]")

        elif choice == "4":
            new_due = get_due_date()
            cursor.execute("UPDATE tasks SET due_date = %s WHERE title = %s", (new_due, task_title))
            conn.commit()
            console.print("[bold green]✓ Due date updated.[/bold green]")

        elif choice == "5":
            break
        else:
            console.print("[red]Invalid option.[/red]")


# ── Mark Task Status ───────────────────────────────────────────────────────────

def mark_status():
    console.print("\n[bold cyan]── Mark Task Status ──[/bold cyan]")

    cursor.execute(
        "SELECT title, category, priority, status, due_date, created_at FROM tasks ORDER BY FIELD(status,'Pending','In Progress','Done'), FIELD(priority,'High','Medium','Low')"
    )
    results = cursor.fetchall()
    if not results:
        console.print("[red]No tasks found.[/red]")
        return

    print_tasks(results)

    try:
        sno = int(input("\nEnter S.No of task to update status: ").strip())
        if sno < 1 or sno > len(results):
            console.print("[red]Invalid S.No.[/red]")
            return
    except ValueError:
        console.print("[red]Invalid input.[/red]")
        return

    task_title = results[sno - 1][0]
    new_status = pick_from_list("New Status", STATUSES)

    cursor.execute("UPDATE tasks SET status = %s WHERE title = %s", (new_status, task_title))
    conn.commit()

    icon = "✓" if new_status == "Done" else "→"
    console.print(f"[bold green]{icon} '{task_title}' marked as {new_status}.[/bold green]")


# ── Delete Task ────────────────────────────────────────────────────────────────

def delete_task():
    console.print("\n[bold red]── Delete Task ──[/bold red]")

    cursor.execute(
        "SELECT title, category, priority, status, due_date, created_at FROM tasks ORDER BY FIELD(priority,'High','Medium','Low')"
    )
    results = cursor.fetchall()
    if not results:
        console.print("[red]No tasks found.[/red]")
        return

    print_tasks(results)

    try:
        sno = int(input("\nEnter S.No of task to delete: ").strip())
        if sno < 1 or sno > len(results):
            console.print("[red]Invalid S.No.[/red]")
            return
    except ValueError:
        console.print("[red]Invalid input.[/red]")
        return

    task_title = results[sno - 1][0]
    confirm = input(f"Are you sure you want to delete '{task_title}'? (y/n): ").strip().lower()
    if confirm != "y":
        console.print("[yellow]Cancelled.[/yellow]")
        return

    cursor.execute("DELETE FROM tasks WHERE title = %s", (task_title,))
    conn.commit()
    console.print(f"[bold green]✓ Task '{task_title}' deleted.[/bold green]")


# ── Main Loop ──────────────────────────────────────────────────────────────────

def main():
    console.print(Panel(
        "[bold cyan]Welcome to CLI To-Do List[/bold cyan]\n"
        "[white]Stay organized. Get things done.[/white]",
        border_style="cyan"
    ))

    # Overdue reminder on startup
    cursor.execute(
        "SELECT COUNT(*) FROM tasks WHERE due_date < %s AND status != 'Done'",
        (date.today(),)
    )
    overdue_count = cursor.fetchone()[0]
    if overdue_count:
        console.print(f"[bold red]You have {overdue_count} overdue task(s)![/bold red]")

    # Due today reminder
    cursor.execute(
        "SELECT COUNT(*) FROM tasks WHERE due_date = %s AND status != 'Done'",
        (date.today(),)
    )
    due_today = cursor.fetchone()[0]
    if due_today:
        console.print(f"[bold yellow]{due_today} task(s) due today.[/bold yellow]")

    while True:
        display_main_menu()
        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_task()
        elif choice == "2":
            view_tasks()
        elif choice == "3":
            update_task()
        elif choice == "4":
            delete_task()
        elif choice == "5":
            mark_status()
        elif choice == "6":
            console.print("\n[bold cyan]Goodbye! Stay productive.[/bold cyan]\n")
            cursor.close()
            conn.close()
            break
        else:
            console.print("[red]Invalid option. Please try again.[/red]")

if __name__ == "__main__":
    main()
