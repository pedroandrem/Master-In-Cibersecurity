from dataclasses import asdict
from command import BaseCommand

class AllItemsCommand(BaseCommand):
    def __init__(self, commands: list[BaseCommand], required_fields: list[str] = None):
        super().__init__(
            name="allitems",
            usage="/allitems",
            minArgs=0,
            description="Show all listed items"
        )
        self.commands = commands
        self.required_fields = required_fields or []

    def execute(self, args: list[str], peer_sub=None, room=None, emit_func=None, lock=None, auction_items=None):
        items = {}
        print("Hello inside execute all items command")

 
        with lock:
            items = {
                item_name: item
                for item_name, item in auction_items.items()
                
            }
 
        # Emit to the client's room (or sid)
        items_dicts = {name: item.to_dict() for name, item in items.items()}
        if emit_func:
            emit_func("all_listed_items", items_dicts, room=room)