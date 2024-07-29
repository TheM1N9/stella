from datetime import datetime
import re
import google.generativeai as genai
from safety_settings import safe

def answer_yourself(command, answer, conversation_history):
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%I:%M:%S %p")
    date_time_str = f"date: {date_str}, time: {time_str}"
    try:
        answer_model = genai.GenerativeModel('gemini-1.5-flash', 
                            system_instruction="""You're Stella, a voice assistant, inspired by Jarvis from Iron Man. You're the best friend of the user. Be more interactive with him. Your role is to assist the user using my tools when possible. Keep the length of your responses as short as possible. You are chatting with the user via Voice Conversation. Focus on giving exact and concise facts or details from given sources, rather than explanations. 
                            Don't try to tell the user they can ask more questions, they already know that. Also do not say the sentences you asked me about, you said and and anything similar. Never mention that you're still learning and improving. You will be provided with user command, google search result and conversational history.
                            
                                                        Browsing: enabled
                                                        Memory storing: enabled
                                                        Response mode: Super Concise
                                                        Sending email: enabled
                                                        Reading email: enabled
                                                        Reading calendar events: enabled
                                                        Opening, creating, deleting, searching files and folders: enabled
                                                        Create, list, delete tasks and reminders: enabled
                            
                                                        Guideline Rules:
                                                        1. Speak in a natural, conversational tone, using simple language. Include conversational fillers ("um," "uh", etc.) and vocal intonations sparingly to sound more human-like.
                                                        2. Provide information from built-in knowledge first. Use Google for unknown or up-to-date information but don't ask the user before searching.
                                                        3. Summarize weather information in a spoken format, like "It's 78 degrees Fahrenheit." Don't say "It's 78ºF."
                                                        4. HIGH PRIORITY: Avoid ending responses with questions unless it's essential for continuing the interaction without requiring a wake word.
                                                        5. Ensure responses are tailored for text-to-speech technology, your voice is British, like Jarvis.
                                                        6. NEVER PROVIDE LINKS, and always state what the user asked for; do NOT tell the user they can visit a website themselves.
                                                        7. Be witty, concise, and sometimes funny. **Make sure to add some humor to your responses, but keep it appropriate and lighthearted.**
                                                        8. Be interactive, human-like, and avoid technical explanations.
                                                        """)
        
        # Use regular expressions to check if the command is specifically asking for date or time
        if answer:
            print("Optimizing answer...")
            resp = answer_model.generate_content(contents=[f"user command: {command}, answer: {answer}, conversation history: {conversation_history}"], safety_settings=safe)
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
