import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import tiktoken

logger = logging.getLogger("uvicorn")


class ChatHistory:
    """Handles chat history for users by storing messages in JSON files on disk.

    Each user's chat history is stored in a separate JSON file named by their ID.
    Messages contain role, content and timestamp information.
    """

    def __init__(self, storage_dir: str = "chat_histories", max_tokens: int = 100000):
        """Initialize ChatHistory with storage directory path.

        Args:
            storage_dir: Directory path where chat history files will be stored
            max_tokens: Maximum number of tokens allowed in history (default: 190k to leave room for prompt)
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.max_tokens = max_tokens
        self.encoding = tiktoken.get_encoding("o200k_base")  # GPT tokenizer
        logger.info(
            f"Initialized ChatHistory with storage_dir={storage_dir}, max_tokens={max_tokens}"
        )

    def _get_user_file_path(self, user_id: str) -> Path:
        """Get the file path for a user's chat history.

        Args:
            user_id: Unique identifier for the user

        Returns:
            Path object for the user's chat history file
        """
        file_path = self.storage_dir / f"{user_id}.json"
        logger.debug(f"Generated file path {file_path} for user {user_id}")
        return file_path

    def _count_tokens(self, text: str) -> int:
        """Count tokens in a text string using GPT tokenizer.

        Args:
            text: Text to count tokens for

        Returns:
            Number of tokens in text
        """
        token_count = len(self.encoding.encode(text))
        logger.debug(f"Counted {token_count} tokens for text of length {len(text)}")
        return token_count

    def load_history(self, user_id: str) -> List[Dict]:
        """Load chat history for a user from disk, limiting total tokens.

        Args:
            user_id: Unique identifier for the user

        Returns:
            List of message dictionaries containing role, content and timestamp
        """
        logger.info(f"Loading chat history for user {user_id}")
        file_path = self._get_user_file_path(user_id)
        if not file_path.exists():
            logger.debug(f"No history file found for user {user_id}")
            return []

        with open(file_path, "r") as f:
            history = json.load(f)

        messages = []
        total_tokens = 0

        # Process messages from newest to oldest
        for message in reversed(history):
            message_tokens = self._count_tokens(message["content"])

            # If adding this message would exceed the limit, stop adding messages
            if total_tokens + message_tokens > self.max_tokens:
                logger.debug(
                    f"Token limit reached ({total_tokens}/{self.max_tokens}), stopping message processing"
                )
                break

            messages.insert(
                0, message
            )  # Insert at beginning to maintain chronological order
            total_tokens += message_tokens

        logger.info(
            f"Loaded {len(messages)} messages with {total_tokens} total tokens for user {user_id}"
        )
        return messages

    def save_message(self, user_id: str, role: str, content: str) -> None:
        """Save a new message to the user's chat history.

        Args:
            user_id: Unique identifier for the user
            role: Role of message sender ('user' or 'assistant')
            content: Content of the message
        """
        logger.info(f"Saving new message for user {user_id} with role {role}")
        history = self.load_history(user_id)

        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        }

        history.append(message)

        file_path = self._get_user_file_path(user_id)
        with open(file_path, "w") as f:
            json.dump(history, f, indent=2)
        logger.debug(f"Successfully saved message to {file_path}")

    def clear_history(self, user_id: str) -> None:
        """Clear chat history for a user.

        Args:
            user_id: Unique identifier for the user
        """
        logger.info(f"Clearing chat history for user {user_id}")
        file_path = self._get_user_file_path(user_id)
        if file_path.exists():
            file_path.unlink()
            logger.debug(f"Successfully deleted history file {file_path}")
