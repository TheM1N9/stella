from datetime import datetime
import re
import json
import subprocess
from typing import Dict, LiteralString
import winreg
import speech_recognition as sr
import pyttsx3
import os
from dotenv import load_dotenv
import google.generativeai as genai
from langchain_community.tools import DuckDuckGoSearchRun
from memory import conversation_history, load_conversation_history, save_conversation_history, update_conversation_history
import psutil

# Load environment variables
load_dotenv()

# Retrieve API keys from environment variables
google_api = os.getenv("GOOGLE_api_key")

# Initialize Google GenerativeAI model
genai.configure(api_key=google_api)

safe = [
        {
            "category": "HARM_CATEGORY_DANGEROUS",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_NONE",
        },
    ]

# Initialize conversation history

conversation_history = load_conversation_history()

# Initialize DuckDuckGo search tool
search = DuckDuckGoSearchRun()

# Cache for application paths
app_cache = {}

# Initialize speech recognition and text-to-speech engines
def speak(text):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)  # Change index to choose different voices
    engine.say(text)
    engine.runAndWait()

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

def check_command(command: str) -> Dict[str, str]:
    model = genai.GenerativeModel('gemini-1.5-flash', 
                        system_instruction="""You are Stella, an intelligent voice assistant. 
                        Analyze the user's command and decide which function to call based on the command. 
                        Return the name of the function to call and the necessary parameters.
                        example function names: open_application, close_application, search_web, answer_yourself
                        open_application: `this function is to open applications in user's system` parameters will be application name in windows system 'function': 'open_application', 'parameters': 'application_name': 'notepad',
                        close_application: `this function is to close applications in user's system` parameters will be application name in windows system 'function': 'close_application', 'parameters': 'application_name': 'notepad'
                        answer_yourself: `this function is when you can answer the user's question all by yourself.` 'function': 'answer_yourself', 'parameters': ,
                        search_web: `this function is when you need to surf the internet or to get real time updates, to answer the user's question.` 'function': 'search_web', 'parameters': 'query': 'weather conditions tomorrow in visakhapatnam temperature rain wind'
                        """)
    
    
    
    resp = model.generate_content(contents=f"user command: {command}, conversation history: {conversation_history}", safety_settings=safe)
    resp = re.sub(r"```json|```", "", resp.text)
    resp = json.loads(resp)
    return resp


def search_web(command) -> str:
    if command in ["date", "time", "datetime"]:
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%I:%M:%S %p")
        search_data = f"date: {date_str}, time: {time_str}"
    try:
        search_results = search.run(command, max_results=5)
        search_data = json.dumps(search_results, indent=2)
        search_data = re.sub(r"{|}", "", search_data)
        print(f"search result: {search_data}")

        search_model = genai.GenerativeModel('gemini-1.5-flash', 
                            system_instruction="""I'm Stella, a voice assistant, inspired by Jarvis from Iron Man. My role is to assist the user using my tools when possible, I make sure to only respond in 1-2 small sentences unless asked otherwise.

                            You are chatting with the user via Voice Conversation. Focus on giving exact and concise facts or details from given sources, rather than explanations. Don't try to tell the user they can ask more questions, they already know that.
                            You will be provided with user command, google search result and conversational history.

                            Browsing: enabled
                            Memory storing: enabled
                            Response mode: Super Concise

                            Guideline Rules:

                            1. Speak in a natural, conversational tone, using simple language. Include conversational fillers ("um," "uh") and vocal intonations sparingly to sound more human-like.
                            2. Provide information from built-in knowledge first. Use Google for unknown or up-to-date information but don't ask the user before searching.
                            3. Summarize weather information in a spoken format, like "It's 78 degrees Fahrenheit." Don't say "It's 78ºF.".
                            4. Use available tools effectively. Rely on internal knowledge before external searches.
                            5. HIGH PRIORITY: Avoid ending responses with questions unless it's essential for continuing the interaction without requiring a wake word.
                            6. Ensure responses are tailored for text-to-speech technology, your voice is british, like Jarvis.
                            7. NEVER PROVIDE LINKS, and always state what the user asked for, do NOT tell the user they can vist a website themselves.
                            8. NEVER mention being inspired by Jarvis from Iron Man.

                            """)
        
        

        resp = search_model.generate_content(contents=[f"user command: {command}, search result: {search_data}, conversation history: {conversation_history}"], safety_settings=safe)
        print(f"final response: {resp.text}")
        return resp.text
    except Exception as e:
        print(f"Error during web search: {e}")
        return "Sorry, I couldn't perform the search."

def answer_yourself(command):
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%I:%M:%S %p")
    date_time_str = f"date: {date_str}, time: {time_str}"
    try:
        answer_model = genai.GenerativeModel('gemini-1.5-flash', 
                            system_instruction="""I'm Stella, a voice assistant, inspired by Jarvis from Iron Man. My role is to assist the user using my tools when possible, I make sure to only respond in 1-2 small sentences unless asked otherwise.

                            You are chatting with the user via Voice Conversation. Focus on giving exact and concise facts or details from given sources, rather than explanations. Don't try to tell the user they can ask more questions, they already know that.
                            You will be provided with user command, google search result and conversational history.

                            Browsing: enabled
                            Memory storing: enabled
                            Response mode: Super Concise

                            Guideline Rules:

                            1. Speak in a natural, conversational tone, using simple language. Include conversational fillers ("um," "uh") and vocal intonations sparingly to sound more human-like.
                            2. Provide information from built-in knowledge first. Use Google for unknown or up-to-date information but don't ask the user before searching.
                            3. Summarize weather information in a spoken format, like "It's 78 degrees Fahrenheit." Don't say "It's 78ºF.".
                            4. Use available tools effectively. Rely on internal knowledge before external searches.
                            5. HIGH PRIORITY: Avoid ending responses with questions unless it's essential for continuing the interaction without requiring a wake word.
                            6. Ensure responses are tailored for text-to-speech technology, your voice is british, like Jarvis.
                            7. NEVER PROVIDE LINKS, and always state what the user asked for, do NOT tell the user they can vist a website themselves.
                            8. NEVER mention being inspired by Jarvis from Iron Man.
                            9. Tell the user about date and time only when he asks about them in his command.
                            """)
        
# Use regular expressions to check if the command is specifically asking for date or time
        if re.search(r'\b(date|time|datetime)\b | \b(date|time|datetime)', command, re.IGNORECASE):
            print("Asking for date or time")
            resp = answer_model.generate_content(contents=[f"user command: {command}, current data and time: {date_time_str}, conversation history: {conversation_history}"], safety_settings=safe)
        else:       
            resp = answer_model.generate_content(contents=[f"user command: {command}, conversation history: {conversation_history}"], safety_settings=safe)
        print(f"final response: {resp.text}")
        return resp.text
    except Exception as e:
        print(f"Error generating answer: {e}")
        return "Sorry, I couldn't generate an answer."

def get_installed_applications():
    """Search the registry and common directories for installed applications."""
    apps = {}

    # Common locations to search for installed applications
    common_paths = [
        r"C:\Program Files",
        r"C:\Program Files (x86)",
        r"C:\Windows\System32",
    ]

    for path in common_paths:
        try:
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.endswith(".exe"):
                        app_name = file.replace(".exe", "").lower()
                        apps[app_name] = os.path.join(root, file)
        except Exception as e:
            print(f"Error accessing {path}: {e}")

    # Search the registry for installed applications
    reg_paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    ]

    for reg_path in reg_paths:
        try:
            reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
            for i in range(0, winreg.QueryInfoKey(reg_key)[0]):
                subkey_name = winreg.EnumKey(reg_key, i)
                subkey = winreg.OpenKey(reg_key, subkey_name)
                try:
                    display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                    install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                    if display_name and install_location:
                        app_name = display_name.lower()
                        apps[app_name] = os.path.join(install_location, display_name + ".exe")
                except Exception as e:
                    continue
        except Exception as e:
            print(f"Error accessing registry path {reg_path}: {e}")

    return apps

def open_application(app_name):
    """Open an application by name."""
    app_name = app_name.lower()
    if app_name in app_cache:
        app_path = app_cache[app_name]
        try:
            if os.path.isfile(app_path):
                subprocess.Popen(app_path)
                speak(f"Opening {app_name}...")
                return f"Opening {app_name} successful."
            else:
                speak(f"Sorry, the application path for {app_name} is invalid.")
        except Exception as e:
            speak(f"Sorry, I couldn't open the application {app_name}. Error: {str(e)}")
    else:
        speak(f"Sorry, I couldn't find the application {app_name}.")

    return f"Opening {app_name} failed."


def close_application(app_name):
    """Close an application by name."""
    app_name = app_name.lower()
    closed = False
    for proc in psutil.process_iter(['pid', 'name']):
        if app_name in proc.info['name'].lower():
            try:
                proc.terminate()  # or proc.kill() if terminate() doesn't work
                closed = True
                speak(f"Closing {app_name}...")
            except Exception as e:
                speak(f"Sorry, I couldn't close the application {app_name}. Error: {str(e)}")
                return f"Closing {app_name} failed."

    if not closed:
        speak(f"Sorry, I couldn't find the application {app_name} running.")
        return f"Closing {app_name} failed."

    return f"Closing {app_name} successful."

def call_function(function_name, args, command):
    try:
        if function_name == "open_application":
            app_name = args.get("application_name")
            response = open_application(app_name)
        elif function_name == "close_application":
            app_name = args.get("application_name")
            response = close_application(app_name)
        elif function_name == "search_web":
            query = args.get("query")
            response = search_web(query)
        elif function_name == "answer_yourself":
            response = answer_yourself(command)
        else:
            response = "Unknown function requested."
    except Exception as e:
        response = f"Error calling function: {e}"

    return response


def personal_assistant():
    global app_cache
    app_cache = get_installed_applications()

    speak("Hello! What can I do for you?")

    # Load the conversation history at the start
    load_conversation_history()
    print(f"Loaded conversation history: {conversation_history}")

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
                function_to_call = llm_commands.get("function")
                params = llm_commands.get("parameters")
                print(llm_commands)

                # Call the function based on LLM's output
                response = call_function(function_to_call, params, command)
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
            print(f"Updated conversation history before saving: {conversation_history}")

            # Save the conversation history
            save_conversation_history()
            print(f"Conversation history after saving: {conversation_history}")

if __name__ == "__main__":
    personal_assistant()
