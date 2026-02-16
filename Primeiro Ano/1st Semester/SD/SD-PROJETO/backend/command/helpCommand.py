from dataclasses import dataclass, field, asdict
import re
from datetime import datetime
import shlex
from flask_socketio import SocketIO, emit

from command import BaseCommand

class HelpCommand(BaseCommand):    
    def __init__(self, commands: list[BaseCommand]):
        super().__init__(
            name="help", 
            usage="/help [command]", 
            minArgs=0, 
            description="Show available commands or info about a specific command"
        )
        self.commands = commands

    def execute(self, args: list[str], peer_sub=None, room=None, emit_func=None, lock=None, auction_items=None):
        if args:
            command_name:str = args[0].lower()
            cmd = next((c for c in self.commands if c.name == command_name), None)
            if cmd:
                emit_func("single_command", asdict(cmd), room=room)
        else:
            for cmd in self.commands:
                emit_func('single_command', asdict(cmd), room=room)