import re
import json
import subprocess
import winreg
import speech_recognition as sr
import pyttsx3
import os
from dotenv import load_dotenv
import google.generativeai as genai
from langchain_community.tools import DuckDuckGoSearchRun

# Load environment variables
load_dotenv()

# Retrieve API keys from environment variables
google_api = os.getenv("GOOGLE_api_key")

# Initialize Google GenerativeAI model
genai.configure(api_key=google_api)
model = genai.GenerativeModel('gemini-1.5-flash', 
                        system_instruction="""You are Stella, an intelligent voice assistant. 
                        Analyze the user's command and decide which function to call based on the command. 
                        Return the name of the function to call and the necessary parameters.
                        example function names: open_application, search_web, answer_yourself
                        open_application: `this function is to open applications in user's system`,
                        answer_yourself: `this function is when you can answer the user's question all by yourself.`,
                        search_web: `this function is when you need to surf the internet or to get real time updates, to answer the user's question.`
                        """)

# Initialize conversation history
conversation_history = []

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

def search_web(command):
    try:
        search_results = search.run(command, max_results=5)
        search_data = json.dumps(search_results, indent=2)
        search_data = re.sub(r"{|}", "", search_data)
        print(f"search result: {search_data}")

        search_model = genai.GenerativeModel('gemini-1.5-flash', 
                            system_instruction="""You are Stella, an intelligent voice assistant.
                            You'll be provided with the user command, the online search results for the command, and the conversation history. Generate an answer based on them.
                            user command: {command},
                            search result: {search_data},
                            conversation history: {conversation_history}
                            """)

        resp = search_model.generate_content([f"user command: {command}, search result: {search_data}, conversation history: {conversation_history}"])
        print(f"final response: {resp.text}")
        return resp.text
    except Exception as e:
        print(f"Error during web search: {e}")
        return "Sorry, I couldn't perform the search."

def answer_yourself(command):
    try:
        answer_model = genai.GenerativeModel('gemini-1.5-flash', 
                            system_instruction="""You are Stella, an intelligent voice assistant. Keep your answers short and simple.
                            You'll be provided with the user command and the conversation history. Generate an answer based on them.
                            """)

        resp = answer_model.generate_content([f"user command: {command}, conversation history: {conversation_history}"])
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

def call_function(function_name, args, command):
    try:
        if function_name == "open_application":
            app_name = args.get("application_name")
            response = open_application(app_name)
        elif function_name == "search_web":
            query = args.get("query")
            response = search_web(query)
        elif function_name == "answer_yourself":
            # text = args.get("text", command)
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

    while True:
        command = listen()

        if "stop" in command:
            speak("Goodbye!")
            break
        elif "hello" in command:
            speak("Hi there!")
        elif "your name" in command:
            speak("I am Stella.")
        else:
            try:
                # Add the command to the conversation history
                conversation_history.append(f"user command: {command}")

                resp = model.generate_content(command)
                resp = re.sub(r"```json|```", "", resp.text)
                resp = json.loads(resp)
                function_to_call = resp.get("function")
                params = resp.get("parameters")
                print(resp)

                # Call the function based on LLM's output
                response = call_function(function_to_call, params, command)
                response = remove_asterisks(response)
                speak(response)

                conversation_history.append(f"response: {response}")

            except json.JSONDecodeError as e:
                print(f"Error decoding JSON response: {e}")
                speak("Sorry, I couldn't process the command.")
            except Exception as e:
                print(f"Error processing command: {e}")
                speak("Sorry, I couldn't process the command.")

if __name__ == "__main__":
    personal_assistant()
