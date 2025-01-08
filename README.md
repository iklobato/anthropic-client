# Anthropic Terminal Client

A command-line interface for interacting with Anthropic's Claude AI models, featuring session management and conversation history.

## Features

- Interactive terminal-based chat interface with Claude
- Session management for organizing multiple conversations
- Real-time streaming of Claude's responses
- Conversation history tracking and persistence
- Rich text formatting for improved readability
- Easy session switching and creation

- ## Screenshots
![Screenshot 2025-01-08 at 16 48 10](https://github.com/user-attachments/assets/d16a6e11-6df1-4160-b424-9e19dc43309b)
![Screenshot 2025-01-08 at 16 48 18](https://github.com/user-attachments/assets/c2e8776f-41fc-4bcf-857b-9da21927e65d)


## Prerequisites

- Python 3.7+
- Anthropic API key
- uv (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/anthropic-client.git
cd anthropic-client
```

2. Install dependencies using uv:
```bash
uv install
```

3. Set up your Anthropic API key as an environment variable:
```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

## Usage

Run the client:
```bash
python chat.py
```

### Available Commands

During chat:
- **Send**: Send your message to Claude
- **Switch Session**: Switch to a different conversation or create a new one
- **New Session**: Start a fresh conversation
- **Exit**: Close the application

### Session Management

- Sessions are automatically saved to `sessions.json`
- Each session stores:
  - Conversation history
  - Creation timestamp
  - First and last messages
  - Message count
- The 10 most recent sessions are available for quick access

## Features in Detail

### Real-time Response Streaming
Watch Claude's responses appear in real-time with a typing-like effect, complete with markdown formatting for code blocks and other structured content.

### Rich Formatting
- User messages in blue
- Claude's responses in purple
- Markdown rendering for code blocks and formatting
- Loading spinner during response generation

### Session History
- Automatic saving of all conversations
- Easy browsing of previous sessions
- Quick session switching without losing context
- Chat logs stored in `chat.log`

## Project Structure
```
.
├── README.md         # Project documentation
├── chat.log         # Application logging file
├── chat.py          # Main application code
├── pyproject.toml   # Project dependencies and metadata
├── sessions.json    # Stored conversation sessions
└── uv.lock          # Lock file for dependencies
```

## Development

The project uses several key Python libraries:
- `anthropic`: Official Anthropic API client
- `rich`: Terminal formatting and markdown rendering
- `inquirer`: Interactive command-line user interfaces
- `dataclasses`: Structured data management

Package management is handled through `pyproject.toml` and uses `uv` for dependency management.

## Contributing

Feel free to submit issues and pull requests for bug fixes or new features.

## License

This project is open source and available under the MIT License.
