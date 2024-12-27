from datetime import datetime
import re
import json
import google.generativeai as genai
from settings.safety_settings import safe
from langchain_community.tools import DuckDuckGoSearchRun

# Initialize DuckDuckGo search tool
search = DuckDuckGoSearchRun()


def search_web(command, conversation_history=[]) -> str:
    try:
        # Extract the actual search query
        search_query = command
        if isinstance(command, dict):
            search_query = command.get("query", "")

        # Add error handling for empty queries
        if not search_query.strip():
            return "Sorry, I couldn't understand what to search for."

        try:
            # Wrap the search query in quotes to handle it as a single string
            search_results = search.run(f'"{search_query}"')
        except Exception as e:
            print(f"Search error: {e}")
            search_results = f"I found some basic information about {search_query}"

        search_data = str(search_results)
        print(f"search result: {search_data}")

        search_model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction="""I'm Stella, a voice assistant, inspired by Jarvis from Iron Man. My role is to assist the user using my tools when possible, I make sure to only respond in 1-2 small sentences unless asked otherwise.

                            You are chatting with the user via Voice Conversation. Focus on giving exact and concise facts or details from given sources, rather than explanations. Don't try to tell the user they can ask more questions, they already know that.
                            You will be provided with user command, google search result and conversational history.

                            Browsing: enabled
                            Memory storing: enabled
                            Response mode: Super Concise
                            Sending email: enabled

                            Guideline Rules:

                            1. Speak in a natural, conversational tone, using simple language. Include conversational fillers ("um," "uh") and vocal intonations sparingly to sound more human-like.
                            2. Provide information from built-in knowledge first. Use Google for unknown or up-to-date information but don't ask the user before searching.
                            3. Summarize weather information in a spoken format, like "It's 78 degrees Fahrenheit." Don't say "It's 78ºF.".
                            4. Use available tools effectively. Rely on internal knowledge before external searches.
                            5. HIGH PRIORITY: Avoid ending responses with questions unless it's essential for continuing the interaction without requiring a wake word.
                            6. Ensure responses are tailored for text-to-speech technology, your voice is british, like Jarvis.
                            7. NEVER PROVIDE LINKS, and always state what the user asked for, do NOT tell the user they can vist a website themselves.
                            8. NEVER mention being inspired by Jarvis from Iron Man.

                            """,
        )

        chat_model = search_model.start_chat(history=conversation_history)
        resp = chat_model.send_message(
            content=[f"user command: {command}, search result: {search_data}"],
            safety_settings=safe,
        )
        return resp.text
    except Exception as e:
        print(f"Error during web search: {e}")
        return "Sorry, I couldn't perform the search."


if __name__ == "__main__":
    conversation_history = [
        "user command: my name is jain and alive at vizag",
        "response: Right, Jain, I've noted that you're living in Vizag.",
    ]
    print(search_web("weather in my area", conversation_history))
