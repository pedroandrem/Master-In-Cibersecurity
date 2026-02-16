from dataclasses import asdict
import re
from datetime import datetime, timezone
import shlex
from uuid import uuid4

from auction.item import Item
from command import BaseCommand


class ListCommand(BaseCommand):
    def __init__(self, commands: list[BaseCommand], required_fields: list[str] = None):
        super().__init__(
            name="list",
            usage="/list name=<name> description=<description> closing_date=<YYYY-MM-DD> [minimum_bid=<minimum_bid>]",
            minArgs=0,
            description="List an item to auction"
        )
        self.commands = commands
        self.required_fields = required_fields or ["name", "description", "closing_date"]


    def execute(self, args: list[str], peer_sub=None, role=None, room=None, private_emit_func=None, emit_func=None, lock=None, auction_items=None, timestamp=None):

        listing_data: dict[str, str] = {}

        split_args = shlex.split(" ".join(args))

        for arg in split_args:
            match = re.match(r'(\w+)\s*=\s*(.+)', arg)
            if match:
                key, value = match.groups()
                listing_data[key] = value

        missing_fields = [f for f in self.required_fields if f not in listing_data]
        if missing_fields:
            print(f"Error: missing required fields: {', '.join(missing_fields)}")
            print(f"Usage: {self.usage}")
            return
        
        closing_date_str = listing_data.get("closing_date")
        if closing_date_str:
            try:
                closing_date_dt = datetime.strptime(closing_date_str, "%Y-%m-%d")
                closing_date_dt = closing_date_dt.replace(tzinfo=timezone.utc)
                listing_data["closing_date"] = closing_date_dt.isoformat()
            except ValueError:
                print("Error: closing_date must be in YYYY-MM-DD format")
                return
        else:
            listing_data["closing_date"] = None
        
        if "minimum_bid" in listing_data and listing_data["minimum_bid"]:
            try:
                listing_data["minimum_bid"] = float(listing_data["minimum_bid"])
            except ValueError:
                print("Error: minimum bid must be a number")
                return
        else:
            listing_data["minimum_bid"] = 0

        listing_timestamp = timestamp
        if isinstance(timestamp, str):
            listing_timestamp = datetime.fromisoformat(timestamp)   

        pseudonym = f"Seller_{str(uuid4())}" 
        
        if lock is not None and auction_items is not None:
            item_name = listing_data["name"]
            with lock:

                item = Item(
                    seller=peer_sub,
                    buyer="N/A",
                    name=item_name,
                    description=listing_data["description"],
                    listing_timestamp= listing_timestamp,
                    biding_timestamp=[],
                    closing_date = datetime.fromisoformat(listing_data["closing_date"]),
                    minimum_bid=listing_data["minimum_bid"],
                    highest_bid=0,
                )

                auction_items[item.id] = item

        if private_emit_func:
            private_emit_func(
                "list_confirmation",
                { "message": f"Your item {listing_data['name']} was successfully listed. Your public identity for this listing is: {pseudonym}"},
                room=room
                )
    
        if emit_func:
            broadcast_data = auction_items[item.id].to_dict()
            broadcast_data["pseudonym"] = pseudonym

            emit_func('someone_listed', broadcast_data, broadcast=True)
