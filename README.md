# Stella Voice Assistant

Stella is an intelligent voice assistant built using Python. It leverages speech recognition, text-to-speech, and natural language processing to interact with users, perform searches, open applications, and manage various tasks on the user's system.

## Features

- **Voice Interaction**: Stella can listen to user commands and respond using text-to-speech.
- **Open Applications**: Stella can open installed applications on your system.
- **Close Applications**: Stella can close the opened applications on your system.
- **Web Search**: Stella can perform web searches using DuckDuckGo and provide concise results.
- **AI-Powered Answers**: Stella uses Google Generative AI to answer questions and decide which functions to call based on user commands.
- **Send Emails**: Stella can automatically send emails to users (requires authorization each time).
- **Fetch Calendar Events**: Stella can fetch events from your calendar.
- **Contextual Awareness**: Stella remembers context from previous conversations to provide more relevant responses.
- **Task Management**: Stella can manage tasks, including creating, updating, and deleting tasks.
- **File and Folder Management**: Stella can open, create, delete, search, and find files and folders.
- **Reminders**: Stella can set reminders and notify you when it's time.

## Installation

### Prerequisites

- Python 3.7 or higher
- [Google Generative AI](https://ai.google/tools) API Key

### Libraries

Install the necessary Python libraries using `pip`:

```bash
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the root directory of your project and add your API keys:

```env
GOOGLE_api_key=your_google_api_key
```

## Usage

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/them1n9/stella.git
    cd stella
    ```

2. **Run the Assistant**:
    ```bash
    python assistant.py
    ```

3. **Interact with Stella**:
    - **Say "Hello"** to start the conversation.
    - **Ask Stella to open applications** (e.g., "Open Chrome").
    - **Ask questions** (e.g., "What is the weather like today?").
    - **Say "Stop"** to end the conversation.

4. **For Sending Emails**:
    - Set up the Gmail API using OAuth2 authentication. Follow these steps:
        - Set up a [Google Cloud Platform](https://cloud.google.com/) project.
        - Under "APIs and services", enable the Gmail API, Calander API.
        - Create credentials for a Desktop App and download the `credentials.json` file.
        - Store the `credentials.json` file in your project directory.

## Code Overview

### Main Components

- `listen()`: Captures and processes user voice input.
- `speak(text)`: Converts text to speech and responds to the user.
- `open_application(app_name)`: Opens the specified application on the user's system.
- `close_application(app_name)`: Closes the specified application on the user's system.
- `search_web(command)`: Performs a web search and generates a response based on search results.
- `answer_yourself(command)`: Generates an answer based on the user's command using Google Generative AI.
- `send_email(command)`: Sends an email based on the user's command.
- `get_calendar_events()`: Fetches events from the user's calendar.
- `manage_tasks(task_action, task_details)`: Manages tasks based on the user's command.
- `open_folder(folder_path)`: Opens a specified folder on the user's system.
- `create_folder(folder_path)`: Creates a specified folder on the user's system.
- `delete_folder(folder_path)`: Deletes a specified folder on the user's system.
- `search_files_and_folders(query)`: Searches for files and folders based on the user's query.
- `set_reminder(reminder_details)`: Sets a reminder based on the user's command.
- `call_function(function_name, args)`: Determines which function to call based on the command analysis.
- `personal_assistant()`: Main function that runs the assistant, listens for commands, and handles responses.

### Application Handling

Stella maintains a cache of installed applications on the user's system, searches for executables in common directories and registry entries, and attempts to open applications based on user commands.

### Error Handling

The assistant includes error handling to manage cases where commands are not recognized, API responses fail, or application paths are incorrect.

## Customization

You can customize Stella by:

- **Adding More Functions**: Implement additional functions and update the LLM's system instructions to include them.
- **Enhancing NLP**: Improve natural language processing by fine-tuning the AI model or using additional NLP libraries.

## Future Updates for Stella

- [ ] Give it the ability to use mouse and keyboard
- [ ] Add the ability to see
- [ ] Change its memory type
- [ ] Add a command to open the web interface from voice prompt and vice versa
- [ ] Integration with Messaging Apps: Connect Stella with messaging platforms like Slack, Microsoft Teams, or WhatsApp for sending and receiving messages
- [ ] Add Wikipedia integration
- [ ] Periodically search for the latest news and store it as summarized memory without a command
- [ ] Maintain an online presence to stay updated with the current world events


## Contributing

Contributions are welcome! Please open an issue or submit a pull request on [GitHub](https://github.com/TheM1N9/stella).
