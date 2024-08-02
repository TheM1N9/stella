import re
import json
from typing import Dict
import speech_recognition as sr
import os
from dotenv import load_dotenv
import google.generativeai as genai
from features.file_management import create_file, create_folder, delete_file, delete_folder, open_file, open_folder, search_files, search_folders
from memory.memory import load_conversation_history, save_conversation_history, update_conversation_history
from features.open_close_app import open_application, close_application
from features.mail import read_emails, send_email
from features.remainder import list_reminders, create_reminder, start_reminder_thread
from settings.safety_settings import safe
from features.self_response import answer_yourself
from features.internet_search import search_web
from features.get_calendar import get_calendar_events
from features.speak import speak
from features.task_management import complete_task, create_task, delete_task, list_tasks, load_tasks

# Load environment variables
load_dotenv()

# Retrieve API keys from environment variables
google_api = os.getenv("GOOGLE_api_key")

# Initialize Google GenerativeAI model
genai.configure(api_key=google_api)

# Load the conversation history at the start
conversation_history = load_conversation_history()

def listen():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening...")

        # Adjust for ambient noise initially
        recognizer.adjust_for_ambient_noise(source)

        print("Waiting for speech...")

        # Adjust dynamically based on the ambient noise level
        dynamic_threshold = recognizer.energy_threshold

        while True:
            try:
                audio = recognizer.listen(source, timeout=None)
                query = recognizer.recognize_google(audio).lower() # type: ignore
                print(f"You said: {query}")
                return query
            except sr.UnknownValueError:
                print("Sorry, I couldn't understand the audio.")
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")
                return ""
            except sr.WaitTimeoutError:
                dynamic_threshold = min(dynamic_threshold + 500, 4500)
                recognizer.energy_threshold = dynamic_threshold
                print(f"Adjusting dynamic threshold to {dynamic_threshold}")

def remove_asterisks(text):
    # Remove double asterisks from the answer
    return re.sub(r"\*\*|\*", "", text)

def is_valid_email(email):
    """Checks if a given string is a valid email address."""
    regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    match = re.match(regex, email)
    return bool(match)

def check_command(command: str, conversation_history) -> Dict[str, str]:
    model = genai.GenerativeModel('gemini-1.5-flash', 
                        system_instruction = """
                        You are Stella, an intelligent voice assistant. 
                        Analyze the user's command and decide which function to call based on the command. 

                        Return the list of the function in order to complete the user's command.
                        Return the name of the function to call and the necessary parameters. If the parameter is not applicable, leave it as an empty string.
                        The parameters mentioned were the only parameters to the function. Do not add any new parameters which were not mentioned.
                        Example function names: open_application, close_application, search_web, answer_yourself, send_email, get_calendar_events, create_file, delete_file, open_file, create_folder, delete_folder, open_folder, search_file_folder, set_reminder, manage_task.

                        open_application: `This function is to open applications on the user's system` function_name: 'open_application', parameters: 'application_name': 'notepad',
                        close_application: `This function is to close applications on the user's system` function_name: 'close_application', parameters: 'application_name': 'notepad',
                        answer_yourself: `This function is when you can answer the user's question all by yourself, also for writing an email.` function_name: 'answer_yourself', parameters: '',
                        search_web: `This function is when you need to surf the internet or to get real-time updates to answer the user's question.` function_name: 'search_web', parameters: 'query': 'weather conditions tomorrow in Visakhapatnam temperature rain wind',
                        send_email: `This function is to send emails.` function_name: 'send_email', parameters: '',
                        read_emails: `This function is to read emails.` function_name: 'read_emails', parameters: '',
                        get_calendar_events: `This function is to get the events from the calendar.` function_name: 'get_calendar_events', parameters: '',
                        create_file: `This function is to create a file.` function_name: 'create_file', parameters: 'file_path': 'C://stella//appy.py',
                        delete_file: `This function is to delete a file.` function_name: 'delete_file', parameters: 'file_path': 'test.py',
                        open_file: `This function is to open a file.` function_name: 'open_file', parameters: 'file_name': 'text.txt',
                        create_folder: `This function is to create a folder.` function_name: 'create_folder', parameters: 'folder_path': 'testing',
                        delete_folder: `This function is to delete a folder.` function_name: 'delete_folder', parameters: 'folder_path': './/testing1',
                        open_folder: `This function is to open a folder.` function_name: 'open_folder', parameters: 'folder_name': 'stella',
                        search_files: `This function is to search for a file.` function_name: 'search_files', parameters: 'search_query': 'assistant.py',
                        search_folders: `This function is to search for a folder.` function_name: 'search_folders', parameters: 'search_query': 'Stella',
                        create_reminder: `This function is to create a reminder.` function_name: 'create_reminder', parameters: 'reminder_text': '', 'reminder_time': '',
                        list_reminders: `This function is to list the reminders.` function_name: 'list_reminders', parameters: '',
                        create_task: `This function is to create tasks.` function_name: 'create_task', parameters: 'task_name': '',
                        list_tasks: `This function is to list the tasks. function_name: 'list_tasks', `parameters: 'task_number': integer,
                        delete_task: `This function is to delete a task.` function_name: 'delete_task', parameters: 'task_number': integer,
                        complete_task: `This function is to complete a task.` function_name: 'complete_task', parameters: 'task_number': integer

                        The JSON output format:
                        `
                            'function_list': ['open_application', 'close_application', 'search_web', 'send_email'],
                            'open_application': `
                                                    'parameters': `
                                                                    'application_name': 'notepad'
                                                                `
                                                `,
                            'close_application': `
                                                    'parameters': `
                                                                        'application_name': 'spotify'
                                                                    `
                                                `,
                            'search_web': `
                                                    'parameters': `
                                                                    'query': 'weather conditions tomorrow in Visakhapatnam temperature rain wind'
                                                                `
                                                `,
                            'send_email': `
                                                'parameters': ''
                                            `
                        `
                        The output should be in the proper JSON format Ensure you use proper parenthesis in the output, replace ` with parenthesis. Parameters is also a JSON.
                        """
                        ,generation_config={"response_mime_type": "application/json"})
    
    resp = model.generate_content(contents=f"user command: {command}, conversation history: {conversation_history}", safety_settings=safe)
    print(resp.text)
    return json.loads(resp.text)

def call_function(llm_commands_list,function_name,command,conversation_history):
    try:
        if function_name == "open_application":
            params = llm_commands_list.get("open_application", {}).get("parameters", {})
            application_name = params.get("application_name", "")
            response = open_application(application_name)
        elif function_name == "close_application":
            params = llm_commands_list.get("close_application", {}).get("parameters", {})
            application_name = params.get("application_name", "")
            response = close_application(application_name)
        elif function_name == "search_web":
            params = llm_commands_list.get("search_web", {}).get("parameters", {})
            query = params.get("query", "")
            response = search_web(query, conversation_history)
        elif function_name == "answer_yourself":
            response = answer_yourself(command=command, conversation_history=conversation_history, answer="")
        elif function_name == "send_email":
            response = send_email(command=command, conversation_history=conversation_history)
        elif function_name == "read_emails":
            ans = read_emails()
            response = answer_yourself(command=command, conversation_history=conversation_history, answer=ans)
        elif function_name == "get_calendar_events":
            ans = get_calendar_events()
            response = answer_yourself(command=command, conversation_history=conversation_history, answer=ans)
        elif function_name == "create_file":
            params = llm_commands_list.get("create_file", {}).get("parameters", {})
            file_path = params.get("file_path", "")
            response = create_file(file_path)
        elif function_name == "delete_file":
            params = llm_commands_list.get("delete_file", {}).get("parameters", {})
            file_path = params.get("file_path", "")
            response = delete_file(file_path)
        elif function_name == "open_file":
            params = llm_commands_list.get("open_file", {}).get("parameters", {})
            file_name = params.get("file_name", "")
            response = open_file(file_name)
        elif function_name == "create_folder":
            params = llm_commands_list.get("create_folder", {}).get("parameters", {})
            folder_path = params.get("folder_path", "")
            response = create_folder(folder_path)
        elif function_name == "delete_folder":
            params = llm_commands_list.get("delete_folder", {}).get("parameters", {})
            folder_path = params.get("folder_path", "")
            response = delete_folder(folder_path)
        elif function_name == "open_folder":
            params = llm_commands_list.get("open_folder", {}).get("parameters", {})
            folder_name = params.get("folder_name", "")
            response = open_folder(folder_name)
        elif function_name == "search_files":
            params = llm_commands_list.get("search_files", {}).get("parameters", {})
            search_query = params.get("search_query", "")
            response = search_files(search_query)
        elif function_name == "search_folders":
            params = llm_commands_list.get("search_folders", {}).get("parameters", {})
            search_query = params.get("search_query", "")
            response = search_folders(search_query)
        elif function_name == "create_reminder":
            params = llm_commands_list.get("create_reminder", {}).get("parameters", {})
            reminder_text = params.get("reminder_text", "")
            reminder_time = params.get("reminder_time", "")
            response = create_reminder(reminder_text, reminder_time)
        elif function_name == "list_reminders":
            response = list_reminders()
        elif function_name == "create_task":
            params = llm_commands_list.get("create_task", {}).get("parameters", {})
            task_name = params.get("task_name", "")
            response = create_task(task_name)
        elif function_name == "list_tasks":
            response = list_tasks()
        elif function_name == "delete_task":
            params = llm_commands_list.get("delete_task", {}).get("parameters", {})
            task_number = params.get("task_number", 0)
            response = delete_task(task_number)
        elif function_name == "complete_task":
            params = llm_commands_list.get("complete_task", {}).get("parameters", {})
            task_number = params.get("task_number", 0)
            response = complete_task(task_number)
        else:
            response = "Sorry, I can't do that!!"
    except Exception as e:
        response = f"Error calling function: {e}"

    return response

def personal_assistant(user_message=None):
    if user_message:
        command = user_message
    else:
        speak("Hello! What can I do for you?")
        command = listen()

    load_tasks()
    start_reminder_thread()

    update_conversation_history(f"user command: {command}")
    # conversation_history.append(f"user command: {command}")
    
    if not command.strip():
        return "No command received."

    if "stop" in command:
        response = "Goodbye!"
        # speak(response)
        # return response
    elif "hello" in command:
        response = "Hello there!"
        # speak(response)
        # return response
    elif "your name" in command:
        response = "I am Stella."
        # speak(response)
        # return response
    else:
        try:
            llm_commands = check_command(command, conversation_history)
            function_list = llm_commands.get("function_list", [])
            response = ""
            for function_name in function_list:
                response += call_function(llm_commands, function_name, command, conversation_history)
            
            response = remove_asterisks(response)
            # speak(response)
            # return response
        except (Exception, json.JSONDecodeError) as e:
            response = "Sorry, I couldn't process the command."
            print(e)
            # speak(response)
            # return response

    update_conversation_history(f"response: {response}")
    # conversation_history.append(f"response: {response}")
    save_conversation_history()

    return response


if __name__ == "__main__":
    personal_assistant()
