import re
import json
from typing import Dict, Any, List
import speech_recognition as sr
import os
from dotenv import load_dotenv
import google.generativeai as genai
from features.file_management import (
    create_file,
    create_folder,
    delete_file,
    delete_folder,
    open_file,
    open_folder,
    search_files,
    search_folders,
)
from memory.memory import load_conversation_history, update_conversation_history
from features.open_close_app import open_application, close_application
from features.mail import read_emails, send_email
from features.remainder import list_reminders, create_reminder, start_reminder_thread
from settings.safety_settings import safe
from features.self_response import answer_yourself
from features.internet_search import search_web
from features.get_calendar import get_calendar_events
from features.speak import speak
from features.task_management import (
    complete_task,
    create_task,
    delete_task,
    list_tasks,
    load_tasks,
)

# Load environment variables
load_dotenv()

# Retrieve API keys from environment variables
google_api = os.getenv("GOOGLE_api_key")

# Initialize Google GenerativeAI model
genai.configure(api_key=google_api)

safe_settings = safe


def listen():
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True
    recognizer.energy_threshold = 300  # Starting threshold
    recognizer.pause_threshold = 0.8  # Shorter pause detection

    with sr.Microphone() as source:
        print("Listening...")

        try:
            # Shorter adjustment period for ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Waiting for speech...")

            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)

            try:
                query = recognizer.recognize_google(audio).lower()
                print(f"You said: {query}")
                return query
            except sr.UnknownValueError:
                print("Could not understand audio. Please try again.")
                return ""
            except sr.RequestError:
                print("Could not reach Google Speech Recognition service.")
                return ""

        except Exception as e:
            print(f"Error during listening: {e}")
            return ""


def remove_asterisks(text):
    # Remove double asterisks from the answer
    return re.sub(r"\*\*|\*", "", text)


def is_valid_email(email):
    """Checks if a given string is a valid email address."""
    regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    match = re.match(regex, email)
    return bool(match)


def check_command(command: str, conversation_history) -> Dict[str, str]:
    # try:
    # print(f"command: {command}")
    # print(f"conversation_history: {conversation_history}")
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash-001",
        system_instruction="""
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
                        {
                            'function_list': ['open_application', 'close_application', 'search_web', 'send_email'],
                            'open_application': {
                                                    'parameters': {
                                                                    'application_name': 'notepad'
                                                                    }
                                                },
                            'close_application': {
                                                    'parameters': {
                                                                        'application_name': 'spotify'
                                                                    }
                                                },
                            'search_web': {
                                                    'parameters': {
                                                                    'query': 'weather conditions tomorrow in Visakhapatnam temperature rain wind'
                                                                }
                                                },
                            'send_email': {
                                                'parameters': ''
                                            }
                        }
                        The output should be in the proper JSON format Ensure you use proper parenthesis in the output, replace ` with parenthesis. Parameters is also a JSON.
                        """,
        generation_config={"response_mime_type": "application/json"},
    )

    chat_model = model.start_chat(history=conversation_history)
    resp = chat_model.send_message(content=command, safety_settings=safe_settings)
    # print(f"command response: {resp}")
    try:
        return json.loads(resp.text)
    except Exception as e:
        print(f"Error: {e}")
        return {}


# except Exception as e:
#     print(f"Error: {e}")
#     return {}


def call_function(
    llm_commands_list: Dict[str, Any],
    function_name: str,
    command: str,
    conversation_history: List[Dict[str, Any]] = [],
):
    # try:
    # Get the function parameters from the correct structure
    params = llm_commands_list.get(function_name, {}).get("parameters", {})

    if function_name == "open_application":
        application_name = params.get("application_name", "")
        response = open_application(application_name)
    elif function_name == "close_application":
        application_name = params.get("application_name", "")
        response = close_application(application_name)
    elif function_name == "search_web":
        query = params.get("query", "")
        response = search_web(query, conversation_history)
    elif function_name == "answer_yourself":
        response = answer_yourself(
            command=command, conversation_history=conversation_history
        )
    elif function_name == "send_email":
        response = send_email(
            command=command, conversation_history=conversation_history
        )
    elif function_name == "read_emails":
        ans = read_emails()
        response = answer_yourself(
            command=command, conversation_history=conversation_history, answer=ans
        )
    elif function_name == "get_calendar_events":
        response = get_calendar_events()
    elif function_name == "create_file":
        file_path = params.get("file_path", "")
        response = create_file(file_path)
    elif function_name == "delete_file":
        file_path = params.get("file_path", "")
        response = delete_file(file_path)
    elif function_name == "open_file":
        file_name = params.get("file_name", "")
        response = open_file(file_name)
    elif function_name == "create_folder":
        folder_path = params.get("folder_path", "")
        response = create_folder(folder_path)
    elif function_name == "delete_folder":
        folder_path = params.get("folder_path", "")
        response = delete_folder(folder_path)
    elif function_name == "open_folder":
        folder_name = params.get("folder_name", "")
        response = open_folder(folder_name)
    elif function_name == "search_files":
        search_query = params.get("search_query", "")
        response = search_files(search_query)
    elif function_name == "search_folders":
        search_query = params.get("search_query", "")
        response = search_folders(search_query)
    elif function_name == "create_reminder":
        reminder_text = params.get("reminder_text", "")
        reminder_time = params.get("reminder_time", "")
        response = create_reminder(reminder_text, reminder_time)
    elif function_name == "list_reminders":
        response = list_reminders()
    elif function_name == "create_task":
        task_name = params.get("task_name", "")
        response = create_task(task_name)
    elif function_name == "list_tasks":
        response = list_tasks()
    elif function_name == "delete_task":
        task_number = params.get("task_number", 0)
        response = delete_task(task_number)
    elif function_name == "complete_task":
        task_number = params.get("task_number", 0)
        response = complete_task(task_number)
    else:
        response = "Sorry, I can't do that!!"
    # except Exception as e:
    #     response = f"Error calling function: {e}"

    return response


def personal_assistant():

    speak("Hello! What can I do for you?")

    # Load the conversation history at the start
    # Initialize conversation history
    conversation_history = load_conversation_history()

    load_tasks()
    start_reminder_thread()

    while True:
        command = listen()

        if not command.strip():
            continue

        if "stop" == command.lower():
            response = "Goodbye!"
            speak("Goodbye!")
            break
        else:
            try:

                llm_commands = check_command(command, conversation_history)
                # print(type(llm_commands))
                print(llm_commands)
                function_list = llm_commands.get("function_list", [])
                response = ""
                for function_name in function_list:
                    result = call_function(
                        llm_commands_list=llm_commands,
                        function_name=function_name,
                        command=command,
                        conversation_history=conversation_history,
                    )
                    # Convert result to string if it's a list
                    response = response + (
                        str(result) if isinstance(result, list) else result
                    )

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
            update_conversation_history({"role": "user", "parts": [{"text": command}]})
            update_conversation_history(
                {"role": "model", "parts": [{"text": response}]}
            )
            conversation_history.append({"role": "user", "parts": [{"text": command}]})
            conversation_history.append(
                {"role": "model", "parts": [{"text": response}]}
            )


if __name__ == "__main__":
    personal_assistant()
