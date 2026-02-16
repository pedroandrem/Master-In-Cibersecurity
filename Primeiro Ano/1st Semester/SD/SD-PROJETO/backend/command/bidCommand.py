from dataclasses import asdict
import re
from datetime import datetime
from uuid import uuid4

from command import BaseCommand

class BidCommand(BaseCommand):
    def __init__(self, commands: list[BaseCommand], required_fields: list[str] = None):
        super().__init__(
            name="bid",
            usage="/bid id=<id> bid_value=<bid_value>",
            minArgs=0,
            description="Bid on an item"
        )
        self.commands = commands
        self.required_fields = required_fields or ["id", "bid_value"]

    def execute(self, args: list[str], peer_sub=None, role=None, room=None, private_emit_func=None, emit_func=None, lock=None, auction_items=None, timestamp=None):
        listing_data: dict[str, str] = {}

        for arg in args:
            match = re.match(r'(\w+)\s*=\s*(.+)', arg)
            if match:
                key, value = match.groups()
                listing_data[key] = value

        missing_fields = [f for f in self.required_fields if f not in listing_data]
        if missing_fields:
            print(f"Error: missing required fields: {', '.join(missing_fields)}")
            print(f"Usage: {self.usage}")
            return
        
        try:
            listing_data["bid_value"] = float(listing_data["bid_value"])
        except ValueError:
            print("Error: bid value must be a number")
            return
        
        listing_data["description"] = listing_data.get("description", None)

        pseudonym = f"Bidder_{str(uuid4())}" 

        if lock is not None and auction_items is not None:
            item_id = listing_data["id"]

            if item_id not in auction_items:
                 private_emit_func("item_not_available", item_id, room=room)
                 return
            
            # bid_value equal or higher
            if not auction_items[item_id].is_valid_bid(listing_data["bid_value"]): 
                private_emit_func("undervalue_bid", {"message": "Provided bid is lower than last bid made."}, room=room)
                return
            
            bidder = None

            item_bid_ts = auction_items[item_id].get_last_bid_timestamp()
            ts_obj = datetime.fromisoformat(timestamp) 

            if item_bid_ts is None:
                bidder = peer_sub
            elif  ts_obj < item_bid_ts:
                bidder = peer_sub
            else: 
                bidder = auction_items[item_id].get_buyer()
                

            # item last timestamp
            item_ts = auction_items[item_id].get_listing_timestamp()
            
            if item_ts > ts_obj:
                private_emit_func("timestamp_error", {"message": "Provided timestamp is older than the listing timestamp."}, room=room)

            with lock:
                item =  auction_items[item_id]

                item.buyer = bidder
                item.highest_bid = listing_data["bid_value"]
                item.add_biding_timestamp(timestamp)

        if private_emit_func:
            private_emit_func(
                "bid_confirmation",
                { "message": f"Your bidding on {listing_data['id']} was successfully. Your public identity for this biddin is: {pseudonym}"},
                room=room
                )       

        if emit_func:

            broadcast_data = auction_items[item.id].to_dict()
            broadcast_data["pseudonym"] = pseudonym

            emit_func('someone_bided', broadcast_data, broadcast=True)

