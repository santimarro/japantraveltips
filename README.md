# Travel Assistant Telegram Bot

A Telegram bot that helps users with travel-related queries. The bot can provide historical information, travel tips, and answer general questions about destinations.

## Features

- **Intent Classification**: Automatically determines whether your query is about historical information, travel advice, or conversational.
- **Multiple Knowledge Sources**: Uses Wikipedia for historical queries and Wikivoyage for travel-specific information.
- **Contextual Understanding**: Maintains conversation history to understand follow-up questions and references to previous messages.
- **Rich Travel Information**: Get recommendations, tips, and practical travel advice for destinations worldwide.

## Requirements

- Python 3.10+
- A Telegram Bot Token (obtained from [BotFather](https://t.me/botfather))
- A Google API Key with access to the Gemini API

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/travel-assistant-bot.git
cd travel-assistant-bot
```

2. Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file based on the template:

```bash
cp .env.template .env
```

5. Edit the `.env` file and add your Telegram Bot Token and Google API Key.

## Usage

1. Start the bot:

```bash
python -m app.main
```

2. Open Telegram and start a conversation with your bot.

3. Use the following commands:
   - `/start` - Start the bot and get a welcome message
   - `/help` - Show help information
   - `/reset` - Clear your conversation history

4. Ask travel-related questions such as:
   - "What's the history of Tokyo?"
   - "What are the best places to visit in Paris?"
   - "How do I get from Narita airport to Tokyo city center?"
   - "What's the local cuisine like in Barcelona?"

## Project Structure

- `app/`: Main application code
  - `main.py`: Entry point for the application
  - `telegram_bot.py`: Telegram bot implementation
  - `chat_history.py`: Handles conversation history storage and retrieval
  - `llm_service/`: LLM integration services
    - `intent_classifier.py`: Classifies user intents using Gemini
    - `response_generator.py`: Generates responses based on classified intents
    - `travel_llm_service.py`: Main service that coordinates the LLM workflow
- `Wikipedia/`: Modified Wikipedia library with Wikivoyage support

## Architecture

1. User sends a message to the Telegram bot
2. The message and conversation history are passed to the intent classifier
3. The intent classifier determines whether the query is historical, travel-related, or conversational
4. Based on the classification, information is retrieved from Wikipedia, Wikivoyage, or generated directly
5. The response generator creates a human-friendly response
6. The bot sends the response back to the user

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- This project uses a modified version of the [Wikipedia](https://github.com/goldsmith/Wikipedia) library.
- Powered by Google's Gemini API for natural language understanding and generation.
