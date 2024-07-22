# JapanTravelTips API

## Overview

JapanTravelTips is a FastAPI-based Retrieval-Augmented Generation (RAG) system designed to interact with a Language Learning Model (LLM) to generate answers for user queries related to traveling in Japan. The system aims to provide advice, tips, and historical information to users, leveraging a rich knowledge base sourced from the subreddit r/JapanTravelTips and Wikipedia.

## Features

- **Travel Advice**: Get recommendations on transportation, accommodations, dining, and sightseeing.
- **Historical Information**: Query historical data about specific locations, shrines, and cultural landmarks.
- **Real-time Interaction**: Interact with the system in real-time to get immediate responses to your travel-related 
questions.
- **Telegram Bot Integration**: Chat with the system via a Telegram bot that forwards user messages to the API and replies with the LLM-generated responses.


## Knowledge Base

The primary knowledge base for this system is derived from the top 100 posts of the year from the subreddit r/JapanTravelTips, including their top 5 comments. Additionally, the system can query Wikipedia to fetch historical information, providing a comprehensive travel guide experience.

## Example Queries

- "Where can I get a Suica card?"
- "What is the history of the Meiji Shrine?"
- "Can you recommend some good restaurants in Kyoto?"

## Getting Started

### Prerequisites

- Python 3.11+
- Poetry for dependency management

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/japantraveltips.git
    cd japantraveltips
    ```

2. Install dependencies using Poetry:
    ```bash
    poetry install
    poetry shell
    ```

3. Configure environment variables in the `.env` file. Ensure you have the necessary API keys, such as `OPENAI_API_KEY`.

### Generating Embeddings

If you have a `./data` directory with documents, generate the embeddings:
    ```bash
    poetry run generate
    ```


### Running the Development Server

Start the FastAPI development server:
    ```bash
    python main.py
    ```


The API will be available at `http://localhost:8000`.

### API Endpoints

The system provides two main API endpoints:

1. **Streaming Chat Endpoint**:
    ```bash
    curl --location 'localhost:8000/api/chat' \
    --header 'Content-Type: application/json' \
    --data '{ "messages": [{ "role": "user", "content": "Hello" }] }'
    ```

2. **Non-Streaming Chat Endpoint**:
    ```bash
    curl --location 'localhost:8000/api/chat/request' \
    --header 'Content-Type: application/json' \
    --data '{ "messages": [{ "role": "user", "content": "Hello" }] }'
    ```

### Docker

To run the application using Docker:

1. Build the Docker image:
    ```bash
    docker build -t japantraveltips .
    ```

2. Generate embeddings (if applicable):
    ```bash
    docker run \
      --rm \
      -v $(pwd)/.env:/app/.env \
      -v $(pwd)/config:/app/config \
      -v $(pwd)/data:/app/data \
      -v $(pwd)/storage:/app/storage \
      japantraveltips \
      poetry run generate
    ```

3. Start the API:
    ```bash
    docker run \
      -v $(pwd)/.env:/app/.env \
      -v $(pwd)/config:/app/config \
      -v $(pwd)/storage:/app/storage \
      -p 8000:8000 \
      japantraveltips
    ```

### Telegram Bot Integration

A Telegram bot can be connected with this API to facilitate user interaction. The bot receives new messages, sends them through the API, and replies back with the LLM-generated responses. The relevant code for the Telegram bot can be found in the following file: [telegram_bot.py](backend/app/telegram_bot.py)

### Documentation

Access the API documentation at `http://localhost:8000/docs` to explore the available endpoints and their usage.

## Contributing

We welcome contributions to enhance the JapanTravelTips API. Please fork the repository and submit pull requests for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [LlamaIndex](https://www.llamaindex.ai/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [r/JapanTravelTips](https://www.reddit.com/r/JapanTravelTips/)
- [Wikipedia](https://www.wikipedia.org/)
