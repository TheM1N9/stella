import re
import json
from typing import Dict, LiteralString
import speech_recognition as sr
import os
from dotenv import load_dotenv
import google.generativeai as genai
from file_management import create_file, create_folder, delete_file, delete_folder, open_file, open_folder, search_files, search_folders
from memory import load_conversation_history, save_conversation_history, update_conversation_history
from open_close_app import open_application, close_application
from mail import read_emails, send_email
from remainder import list_reminders, create_reminder, start_reminder_thread
from safety_settings import safe
from self_response import answer_yourself
from internet_search import search_web
from get_calendar import get_calendar_events
from speak import speak
from task_management import complete_task, create_task, delete_task, list_tasks, load_tasks

# Load environment variables
load_dotenv()

# Retrieve API keys from environment variables
google_api = os.getenv("GOOGLE_api_key")

# Initialize Google GenerativeAI model
genai.configure(api_key=google_api)

# Initialize conversation history
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

def check_command(command: str) -> Dict[str, str]:
    model = genai.GenerativeModel('gemini-1.5-flash', 
                        system_instruction = """
                        You are Stella, an intelligent voice assistant. 
                        Analyze the user's command and decide which function to call based on the command. 

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
                        create_task: `This function is to create tasks.` function_name: 'create_task', parameters: task_name: '',
                        list_tasks: `This function is to list the tasks. function_name: 'list_tasks', `parameters: task_number: integer,
                        delete_task: `This function is to delete a task.` function_name: 'delete_task', parameters: task_number: integer,
                        complete_task: `This function is to complete a task.` function_name: 'complete_task', parameters: task_number: integer
                        """
                        ,generation_config={"response_mime_type": "application/json"})
    
    resp = model.generate_content(contents=f"user command: {command}, conversation history: {conversation_history}", safety_settings=safe)
    # resp = re.sub(r"```json|```", "", resp.text)
    resp = json.loads(resp.text)
    return resp

def call_function(function_name, args, command, conversation_history):
    try:
        if function_name == "open_application":
            app_name = args.get("application_name", "")
            response = open_application(app_name)
        elif function_name == "close_application":
            app_name = args.get("application_name", "")
            response = close_application(app_name)
        elif function_name == "search_web":
            query = args.get("query", "")
            response = search_web(query, conversation_history)
        elif function_name == "answer_yourself":
            response = answer_yourself(command=command, conversation_history=conversation_history)
        elif function_name == "send_email":
            response = send_email(command=command, conversation_history=conversation_history)
        elif function_name == "read_emails":
            response = read_emails()
        elif function_name == "get_calendar_events":
            response = get_calendar_events()
        elif function_name == "create_file":
            file_path = args.get("file_path", "")
            response = create_file(file_path)
        elif function_name == "delete_file":
            file_path = args.get("file_path", "")
            response = delete_file(file_path)
        elif function_name == "open_file":
            file_name = args.get("file_name", "")
            file_name = re.sub("file", "", file_name)
            file_name = re.sub(" ", "_", file_name)
            response = open_file(file_name)
        elif function_name == "create_folder":
            folder_path = args.get("folder_path", "")
            response = create_folder(folder_path)
        elif function_name == "delete_folder":
            folder_path = args.get("folder_path", "")
            response = delete_folder(folder_path)
        elif function_name == "open_folder":
            folder_name = args.get("folder_name", "")
            folder_name = re.sub("folder", "", folder_name)
            folder_name = re.sub(" ", "_", folder_name)
            response = open_folder(folder_name)
        elif function_name == "search_files":
            search_query = args.get("search_query", "")
            response = search_files(search_query)
        elif function_name == "search_folders":
            search_query = args.get("search_query", "")
            response = search_folders(search_query)
        elif function_name == "create_reminder":
            reminder_text = args.get("reminder_text", "")
            reminder_time = args.get("reminder_time", "")
            response = create_reminder(reminder_text, reminder_time)
        elif function_name == "list_reminders":
            response = list_reminders()
        elif function_name == "create_task":
            action = args.get("task_name", "")
            response = create_task(action)
        elif function_name == "list_tasks":
            response = list_tasks()
        elif function_name == "delete_task":
            task_number = args.get("task_number", "")
            response = delete_task(task_number)
        elif function_name == "complete_task":
            task_number = args.get("task_number", "")
            response = complete_task(task_number)
        else:
            response = "Sorry, I can't do that!!"
    except Exception as e:
        response = f"Error calling function: {e}"

    return response



def personal_assistant():

    speak("Hello! What can I do for you?")

    # Load the conversation history at the start
    load_conversation_history()
    # print(f"Loaded conversation history: {conversation_history}")

    load_tasks()
    start_reminder_thread()

    while True:
        command = listen()
        # Add the command to the conversation history
        update_conversation_history(f"user command: {command}")
        conversation_history.append(f"user command: {command}")
        # print(f"Updated conversation history: {conversation_history}")
        
        if not command.strip():
            continue

        if "stop" in command:
            response = "Goodbye!"
            speak("Goodbye!")
            break
        elif "hello" in command:
            response = "Hello there!"
            speak("Hi there!")
        elif "your name" in command:
            response = "I am Stella."
            speak("I am Stella.")
        else:
            try:
                llm_commands = check_command(command)
                print(type(llm_commands))
                print(llm_commands)
                function_to_call = llm_commands.get("function_name")
                params = llm_commands.get("parameters")
                print(function_to_call)

                # Call the function based on LLM's output
                response = call_function(function_name=function_to_call, args=params, command=command, conversation_history=conversation_history)
                response = remove_asterisks(response)
                speak(response)

            except json.JSONDecodeError as e:
                response = "Sorry, I couldn't process the command."
                print(f"Error decoding JSON response: {e}")
                speak("Sorry, I couldn't process the command.")
            except Exception as e:
                response = "Sorry, I couldn't process the command."
                print(f"Error processing command: {e}")
                speak("Sorry, I couldn't process the command.")

            # Add the response to the conversation history
            update_conversation_history(f"response: {response}")
            conversation_history.append(f"response: {response}")
            # print(f"Updated conversation history before saving: {conversation_history}")

            # Save the conversation history
            save_conversation_history()
            # print(f"Conversation history after saving: {conversation_history}")

if __name__ == "__main__":
    personal_assistant()
