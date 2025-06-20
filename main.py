import json
import os
import time
from datetime import datetime, date, timedelta
from colorama import Fore, Style, init

# Set up terminal color formatting
init(autoreset=True)

DATA_FILE = "tasks.json"
DATE_FORMAT_DISPLAY = "%d/%m/%Y"
DATE_FORMAT_INPUT = "%d/%m/%Y"
DATE_FORMAT_STORAGE = "%Y-%m-%d"

def read_task_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as file:
        return json.load(file)

def write_task_data(task_list):
    with open(DATA_FILE, "w") as file:
        json.dump(task_list, file, indent=4)

def refresh_task_deadlines(task_list):
    today = date.today()
    for task in task_list:
        if task["Status"] == "Pending":
            due = datetime.strptime(task["Due Date"], DATE_FORMAT_STORAGE).date()
            if due < today:
                task["Status"] = "Overdue"
    return task_list

def generate_next_id(task_list):
    return max((task["ID"] for task in task_list), default=0) + 1

def create_task():
    task_list = read_task_data()
    print(Fore.CYAN + "\n--- Add a New Task ---")
    title = input("What is the task? ")
    description = input("Describe it briefly: ")
    deadline = input(f"Due date ({DATE_FORMAT_DISPLAY}): ")
    priority = input("Priority (High / Medium / Low): ").capitalize()

    due_date_obj = datetime.strptime(deadline, DATE_FORMAT_INPUT)
    stored_due_date = due_date_obj.strftime(DATE_FORMAT_STORAGE)

    new_task = {
        "ID": generate_next_id(task_list),
        "Title": title,
        "Description": description,
        "Due Date": stored_due_date,
        "Priority": priority,
        "Status": "Pending",
        "Created At": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Completed At": ""
    }

    task_list.append(new_task)
    write_task_data(task_list)
    print(Fore.GREEN + "✅ Task added successfully!\n")

def export_summary():
    task_list = read_task_data()
    if not task_list:
        print(Fore.YELLOW + "⚠️ No tasks available to export.")
        return

    with open("task_summary.txt", "w", encoding="utf-8") as file:
        file.write("📋 Task Summary Report\n")
        file.write("========================\n\n")
        for t in task_list:
            due_display = datetime.strptime(t["Due Date"], DATE_FORMAT_STORAGE).strftime(DATE_FORMAT_DISPLAY)
            file.write(f"🆔 ID: {t['ID']}\n")
            file.write(f"📝 Title: {t['Title']}\n")
            file.write(f"📅 Due Date: {due_display}\n")
            file.write(f"🎯 Priority: {t['Priority']}\n")
            file.write(f"📌 Status: {t['Status']}\n\n")

    print(Fore.GREEN + "\n✅ Task summary has been successfully saved!")
    print(Fore.CYAN + "📂 You can find it in the current directory as 'task_summary.txt'.\n")

def style_status(status):
    return {
        "Completed": Fore.GREEN,
        "Pending": Fore.YELLOW,
        "Overdue": Fore.RED
    }.get(status, "")

def style_priority(priority):
    return {
        "High": Fore.RED,
        "Medium": Fore.YELLOW,
        "Low": Fore.GREEN
    }.get(priority, "")

def keyword_search():
    task_list = read_task_data()
    keyword = input("Type a keyword to search: ").lower()
    hits = [t for t in task_list if keyword in t["Title"].lower() or keyword in t["Description"].lower()]
    print(Fore.CYAN + "\n======= Search Results =======")
    for t in hits:
        due_display = datetime.strptime(t["Due Date"], DATE_FORMAT_STORAGE).strftime(DATE_FORMAT_DISPLAY)
        print(f'[{t["ID"]}] {t["Title"]} | Due: {due_display} | Priority: {t["Priority"]} | Status: {t["Status"]}')
    print()

def apply_filters():
    task_list = refresh_task_deadlines(read_task_data())
    write_task_data(task_list)

    while True:
        print(Fore.MAGENTA + "\n✨ Filter Options ✨")
        print("""
        1️⃣  View Only Pending Tasks
        2️⃣  View Only Completed Tasks
        3️⃣  View Tasks Due Today
        4️⃣  View Tasks Due Tomorrow
        5️⃣  View Overdue Tasks
        0️⃣  🔙 Return to Main Menu
        """)

        option = input(Fore.YELLOW + "Please enter your choice (0–5): ")
        today = date.today()
        tomorrow = today + timedelta(days=1)

        filtered = []
        title = ""

        if option == "0":
            print(Fore.BLUE + "🔙 Returning to main menu...\n")
            break
        elif option == "1":
            filtered = [t for t in task_list if t["Status"] == "Pending"]
            title = "Pending Tasks"
        elif option == "2":
            filtered = [t for t in task_list if t["Status"] == "Completed"]
            title = "Completed Tasks"
        elif option == "3":
            filtered = [t for t in task_list if t["Due Date"] == today.strftime(DATE_FORMAT_STORAGE)]
            title = "Tasks Due Today"
        elif option == "4":
            filtered = [t for t in task_list if t["Due Date"] == tomorrow.strftime(DATE_FORMAT_STORAGE)]
            title = "Tasks Due Tomorrow"
        elif option == "5":
            filtered = [t for t in task_list if t["Status"] == "Overdue"]
            title = "Overdue Tasks"
        else:
            print(Fore.RED + "❌ Invalid selection. Try again.")
            continue

        print(Fore.CYAN + f"\n======= {title} =======")
        if not filtered:
            print(Fore.YELLOW + "⚠️ No tasks found matching this filter.\n")
        else:
            print("ID | Title                | Due Date   | Priority | Status     | Days Left")
            print("---|----------------------|------------|----------|------------|-----------")
            for t in filtered:
                due = datetime.strptime(t["Due Date"], DATE_FORMAT_STORAGE)
                due_display = due.strftime(DATE_FORMAT_DISPLAY)
                days_left = (due.date() - date.today()).days
                left = f"{days_left} day(s)" if days_left >= 0 else "Past Due"
                print(f'{str(t["ID"]).ljust(3)}| {t["Title"][:20].ljust(22)}| {due_display} | {style_priority(t["Priority"])}{t["Priority"].ljust(8)} | {style_status(t["Status"])}{t["Status"].ljust(10)} | {left}')
            print(Fore.GREEN + f"\n✅ Found {len(filtered)} task(s).\n")

def show_all_tasks():
    task_list = refresh_task_deadlines(read_task_data())
    write_task_data(task_list)

    print("Choose how to sort your list:")
    print("1. By Task ID (Default)")
    print("2. Priority + Status")
    sort_choice = input("Your choice (1/2): ")

    if sort_choice == "2":
        status_order = {"Overdue": 1, "Pending": 2, "Completed": 3}
        priority_order = {"High": 1, "Medium": 2, "Low": 3}
        task_list.sort(key=lambda t: (status_order.get(t["Status"], 4), priority_order.get(t["Priority"], 4)))
    else:
        task_list.sort(key=lambda x: x["ID"])

    print(Fore.CYAN + "\n======= All Tasks =======")
    print("ID | Title                | Due Date   | Priority | Status     | Days Left")
    print("---|----------------------|------------|----------|------------|-----------")

    for t in task_list:
        color_status = style_status(t["Status"])
        color_priority = style_priority(t["Priority"])
        due = datetime.strptime(t["Due Date"], DATE_FORMAT_STORAGE)
        due_display = due.strftime(DATE_FORMAT_DISPLAY)
        days_left = (due.date() - date.today()).days
        left = f"{days_left} day(s)" if days_left >= 0 else "Past Due"
        print(f'{str(t["ID"]).ljust(3)}| {t["Title"][:20].ljust(22)}| {due_display} | {color_priority + t["Priority"].ljust(8)} | {color_status + t["Status"].ljust(10)} | {left}')
    print()

def finish_task():
    task_list = read_task_data()
    try:
        task_id = int(input("Enter task ID to complete: "))
        for task in task_list:
            if task["ID"] == task_id and task["Status"] != "Completed":
                task["Status"] = "Completed"
                task["Completed At"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print("Updating...", end=" ")
                for _ in range(5):
                    print("█", end="", flush=True)
                    time.sleep(0.1)
                print(" ✅ Done!")
                write_task_data(task_list)
                return
        print(Fore.RED + "❌ Task not found or already completed.\n")
    except ValueError:
        print(Fore.RED + "❌ Invalid input. Enter a valid ID number.\n")

def remove_task():
    task_list = read_task_data()
    try:
        task_id = int(input("Enter task ID to delete: "))
        confirm = input("Are you sure you want to delete this task? (y/n): ")
        if confirm.lower() == 'y':
            task_list = [t for t in task_list if t["ID"] != task_id]
            # Reassign IDs
            for idx, task in enumerate(task_list, start=1):
                task["ID"] = idx
            write_task_data(task_list)
            print(Fore.GREEN + "🗑️  Task deleted and IDs updated successfully!\n")
        else:
            print(Fore.YELLOW + "⚠️ Task deletion cancelled.")
    except ValueError:
        print(Fore.RED + "❌ Invalid task ID.\n")

def main():
    print(Fore.MAGENTA + Style.BRIGHT + """
===============================
    📝 SMART TO-DO MANAGER
===============================
""")
    while True:
        print(Fore.BLUE + "\n📋 Menu Options")
        print("1. ➕ Add New Task")
        print("2. ✅ Complete Task")
        print("3. 🗑️  Delete Task")
        print("4. 📂 View All Tasks")
        print("5. 🔍 Filter View")
        print("6. 🔎 Search Tasks")
        print("7. 📄 Export Summary")
        print("8. 🚪 Exit")

        action = input("Choose an option (1-8): ")
        if action == "1":
            create_task()
        elif action == "2":
            finish_task()
        elif action == "3":
            remove_task()
        elif action == "4":
            show_all_tasks()
        elif action == "5":
            apply_filters()
        elif action == "6":
            keyword_search()
        elif action == "7":
            export_summary()
        elif action == "8":
            print(Fore.CYAN + "👋 Thank you for using the To-Do Manager!")
            break
        else:
            print(Fore.RED + "❌ Invalid option. Try again.")

if __name__ == "__main__":
    main()
