# add search feature
# create an interface


import speech_recognition as sr
import pyttsx3
import os
import google.generativeai as genai
from langchain_community.utilities import SerpAPIWrapper

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import json 

load_dotenv()
google_api = os.getenv("GOOGLE_api_key")
serpapi_api = os.getenv("SERPAPI_api_key")
# GOOGLE_API_KEY = genai.configure(api_key="AIzaSyBeXOGSwje-0FKGLR4ZsUROkRtGOp5Lk2A")
# txt_model = genai.GenerativeModel('gemini-pro')

llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=google_api)
custom_prompt = PromptTemplate.from_template("You are an intelligent college professor who excells in all programming languages. Tell me about {topic}.")
custom_chain = LLMChain(llm=llm, prompt=custom_prompt, verbose=True)


# from langchain.agents import load_tools
# tools = load_tools(["serpapi"])
search = SerpAPIWrapper(serpapi_api_key=serpapi_api)

def speak(text):
    engine = pyttsx3.init()
    voices=engine.getProperty('voices')
    engine.setProperty('voice',voices[1].id)
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
            audio = recognizer.listen(source, timeout=None)

            try:
                query = recognizer.recognize_google(audio).lower()
                print(f"You said: {query}")
                return query
            except sr.UnknownValueError:
                # Ignore when no speech is detected
                pass
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")
                return ""
            except sr.WaitTimeoutError:
                # Adjust the threshold dynamically to filter out ambient noise
                dynamic_threshold = min(dynamic_threshold + 500, 4500)
                recognizer.energy_threshold = dynamic_threshold
                print(f"Adjusting dynamic threshold to {dynamic_threshold}")
    
def bold_headings(text):
    # Remove double asterisks from headings
    output = text.replace('**', '')
    return output

def personal_assistant():
    speak("Hello! What can I do for you?")

    # while True:
    #     wake_word = listen()
        
    #     if "hero" in wake_word:
    #         speak("Yes, I'm listening. How can I assist you?")
    #         print("Hola")
    #         break
    #     else:
    #         speak("I'm waiting for the wake word.")
    #         print("hfiaehf")

    while True:
        command = listen()
        
        if "stop" in command:
            speak("Goodbye!")
            break
        elif "your name" in command:
            speak("I am Stella.")
        elif 'search' in command:
            json_data = search.run(command)
            formatted_data = json.dumps(json_data, indent=2)
            # Print the formatted data
            print(formatted_data)
        else:
            try:
                resp = custom_chain.run(topic=command)
                response_with_bold_headings = bold_headings(resp)
                print(response_with_bold_headings)
                speak(response_with_bold_headings)
            except TypeError as te:
                print(f"Error generating content: {te}")

if __name__ == "__main__":
    personal_assistant()

