import json
import re

# Global variable to hold the conversation history
conversation_history = []

def load_conversation_history():
    global conversation_history
    try:
        with open('conversation_history.json', 'r') as file:
            conversation_history = json.load(file)
        print("Conversation history loaded successfully.")
    except FileNotFoundError:
        print("No previous conversation history found.")
    except json.JSONDecodeError:
        print("Error decoding JSON from conversation history.")
    except Exception as e:
        print(f"An unexpected error occurred while loading history: {e}")

    return conversation_history


def save_conversation_history():
    global conversation_history
    # print(f"Saving conversation history: {conversation_history}")
    if not conversation_history:
        print("Warning: Attempting to save an empty conversation history.")
    try:
        with open('conversation_history.json', 'w') as file:
            json.dump(conversation_history, file, indent=4)
        print("Conversation history saved successfully.")
        # Verify if the file has been updated
        with open('conversation_history.json', 'r') as file:
            contents = file.read()
            print("File contents after saving:")
            print(contents)
            if not contents:
                print("Error: File is empty after save.")
    except Exception as e:
        print(f"An error occurred while saving history: {e}")

def update_conversation_history(new_entry):
    global conversation_history
    conversation_history.append(new_entry)
    # print(f"Updated conversation history: {conversation_history}")

if __name__ == "__main__":
    # Example usage
    load_conversation_history()
    update_conversation_history('user command: my name is jain')
    update_conversation_history('response: Hello, Jain.')
    save_conversation_history()