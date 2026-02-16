from dataclasses import dataclass, field, asdict
from typing import List, Dict
import re
from datetime import datetime
import shlex
from flask_socketio import SocketIO, emit

from auction.item import Item


@dataclass(frozen=True)
class BaseCommand:
    name: str = field(default="")
    usage: str = field(default="")
    minArgs: int = field(default=0)
    description: str = field(default="")

    def __post_init__(self):
        if " " in self.name:
            raise ValueError("Command name cannot contain spaces")

    def execute(self, args: List[str], peer_uuid:str = None, emit_func=None):
        if len(args) < self.minArgs:
            print(f"Usage: {self.usage} (requires at least {self.minArgs} arguments)")
            return
        raise NotImplementedError("execute() must be overridden in subclass")