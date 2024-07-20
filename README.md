# Stella Voice Assistant

Stella is an intelligent voice assistant built using Python. It leverages speech recognition, text-to-speech, and natural language processing to interact with users, perform searches, and open applications on the user's system.

## Features

- **Voice Interaction**: Stella can listen to user commands and respond using text-to-speech.
- **Open Applications**: Stella can open installed applications on your system.
- **Close Applications**: Stella can close the opened applications on your system.
- **Web Search**: Stella can perform web searches using DuckDuckGo and provide concise results.
- **AI-Powered Answers**: Stella uses Google Generative AI to answer questions and decide which functions to call based on user commands.

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

## Code Overview

### Main Components

- `listen()`: Captures and processes user voice input.
- `speak(text)`: Converts text to speech and responds to the user.
- `open_application(app_name)`: Opens the specified application on the user's system.
- `close_application(app_name)`: Closes the specified application on the user's system.
- `search_web(command)`: Performs a web search and generates a response based on search results.
- `answer_yourself(command)`: Generates an answer based on the user's command using Google Generative AI.
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

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on [GitHub](https://github.com/TheM1N9/stella).
