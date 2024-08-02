import json

# Load tasks from a file
def load_tasks():
    global tasks
    try:
        with open("memory/tasks.json", "r") as f:
            tasks = json.load(f)
    except FileNotFoundError:
        tasks = []

# Save tasks to a file
def save_tasks():
    global tasks
    with open("memory/tasks.json", "w") as f:
        json.dump(tasks, f)

# Create a new task
def create_task(task_name):
    global tasks
    tasks.append({"task": task_name, "completed": False})
    save_tasks()
    return f"Task '{task_name}' created."

# List all tasks
def list_tasks():
    global tasks
    if not tasks:
        return "No tasks available."
    task_list = "\n".join([f"{i+1}. {task['task']} - {'Completed' if task['completed'] else 'Pending'}" for i, task in enumerate(tasks)])
    print(f"Here are your tasks:\n{task_list}")
    return f"Here are your tasks:\n{task_list}"

# Complete a task
def complete_task(task_number):
    print(task_number)
    try:
        task_number = int(task_number)
    except ValueError:
        return "Invalid task number."
    # task_number = int(task_number)
    global tasks
    if 0 < task_number <= len(tasks):
        tasks[task_number-1]["completed"] = True
        save_tasks()
        return f"Task {task_number} marked as completed."
    return "Invalid task number."

# Delete a task
def delete_task(task_number):
    task_number = int(task_number)
    global tasks
    if 0 < task_number <= len(tasks):
        task_name = tasks.pop(task_number-1)["task"]
        save_tasks()
        return f"Task '{task_name}' deleted."
    return "Invalid task number."

if __name__ == "__main__":
    load_tasks()
    create_task("hello")
    list_tasks()
    complete_task(1)
    list_tasks()
    delete_task(1)
    list_tasks()

