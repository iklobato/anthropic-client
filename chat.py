import os
import sys
import logging
import json
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from anthropic import Anthropic
from rich.console import Console
from rich.markdown import Markdown
from pathlib import Path
import inquirer

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s'
)


@dataclass
class Session:
    id: str
    created_at: str
    history: List[Dict[str, str]]
    first_message: str = ""
    last_message: str = ""
    message_count: int = 0


@dataclass
class TerminalChat:
    client: Anthropic = field(init=False)
    console: Console = field(default_factory=Console)
    history: List[Dict[str, str]] = field(default_factory=list)
    sessions_file: Path = field(default=Path("sessions.json"))
    current_session: Optional[str] = field(default=None)
    sessions: Dict[str, Session] = field(default_factory=dict)

    def __post_init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))
        self.load_sessions()

    def load_sessions(self):
        if self.sessions_file.exists():
            data = json.loads(self.sessions_file.read_text())
            self.sessions = {
                id_: Session(**session_data) for id_, session_data in data.items()
            }

    def save_sessions(self):
        data = {
            id_: {
                "id": session.id,
                "created_at": session.created_at,
                "history": session.history,
                "first_message": session.first_message,
                "last_message": session.last_message,
                "message_count": session.message_count,
            }
            for id_, session in self.sessions.items()
        }
        self.sessions_file.write_text(json.dumps(data, indent=2))

    def create_new_session(self):
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.sessions[session_id] = Session(
            id=session_id, created_at=datetime.now().isoformat(), history=[]
        )
        self.current_session = session_id
        self.history = []
        self.save_sessions()
        return session_id

    def select_session(self):
        def format_session(session):
            datetime_obj = datetime.fromisoformat(session.created_at)
            formatted_time = datetime_obj.strftime("%H:%M:%S")
            first_msg = (
                (session.first_message[:35] + '...')
                if len(session.first_message) > 35
                else session.first_message or '...'
            )
            last_msg = (
                (session.last_message[:35] + '...')
                if len(session.last_message) > 35
                else session.last_message or '...'
            )

            return (
                f"[{formatted_time}] "
                f"Messages: {session.message_count:2d} | "
                f"First: {first_msg:<38} | "
                f"Last: {last_msg}",
                session.id,
            )

        choices = [format_session(s) for s in list(self.sessions.values())[-10:]]
        choices.append(("Create New Session", "new"))

        result = inquirer.prompt(
            [
                inquirer.List(
                    'session',
                    message="Select a session",
                    choices=choices,
                    carousel=True,
                )
            ]
        )

        return result['session'] if result else None

    def display_conversation_history(self):
        if not self.current_session or not self.sessions[self.current_session].history:
            return

        for msg in self.sessions[self.current_session].history:
            if msg["role"] == "user":
                self.console.print("\n[bold blue]You[/bold blue]")
                self.console.print(msg["content"])
            else:
                self.console.print("\n[bold purple]Claude[/bold purple]")
                self.console.print(Markdown(msg["content"]))

    def stream_response(self, response_stream):
        content = []
        with self.console.status("[bold green]Claude is thinking..."):
            for message in response_stream:
                if hasattr(message, 'delta') and hasattr(message.delta, 'text'):
                    content.append(message.delta.text)

        full_response = "".join(content)
        self.console.print(Markdown(full_response))
        return full_response

    def chat(self):
        if not self.current_session:
            self.create_new_session()

        self.console.print("[bold blue]Terminal Claude Chat[/bold blue]")
        self.display_conversation_history()

        while True:
            try:
                answers = inquirer.prompt(
                    [
                        inquirer.Text('message', message="You"),
                        inquirer.List(
                            'action',
                            message="Actions",
                            choices=[
                                ('Send', 'send'),
                                ('Switch Session', 'switch'),
                                ('New Session', 'new'),
                                ('Exit', 'exit'),
                            ],
                            carousel=True,
                        ),
                    ]
                )

                if not answers:
                    continue

                if answers['action'] == 'exit':
                    break
                elif answers['action'] == 'switch':
                    session_id = self.select_session()
                    if session_id == 'new':
                        self.create_new_session()
                    elif session_id:
                        self.current_session = session_id
                        self.history = self.sessions[session_id].history
                        self.display_conversation_history()
                    continue
                elif answers['action'] == 'new':
                    self.create_new_session()
                    continue

                user_input = answers['message']
                current_session = self.sessions[self.current_session]

                if not current_session.first_message:
                    current_session.first_message = user_input

                messages = self.history + [{"role": "user", "content": user_input}]
                self.console.print("\n[bold purple]Claude[/bold purple]")

                stream = self.client.messages.create(
                    model="claude-3-5-sonnet-latest",
                    max_tokens=1024,
                    messages=messages,
                    stream=True,
                )

                response_content = self.stream_response(stream)

                self.history.append({"role": "user", "content": user_input})
                self.history.append({"role": "assistant", "content": response_content})

                current_session.history = self.history
                current_session.last_message = user_input
                current_session.message_count = len(self.history) // 2
                self.save_sessions()

            except KeyboardInterrupt:
                self.console.print("\n[bold red]Exiting...[/bold red]")
                break
            except Exception as e:
                self.console.print(f"\n[bold red]Error: {str(e)}[/bold red]")


def main():
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY not found in environment variables")
        sys.exit(1)
    chat = TerminalChat()
    chat.chat()


if __name__ == "__main__":
    main()
