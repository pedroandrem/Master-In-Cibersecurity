from dataclasses import asdict
from command import BaseCommand

class MyItemsCommand(BaseCommand):
    def __init__(self, commands: list[BaseCommand], required_fields: list[str] = None):
        super().__init__(
            name="myitems",
            usage="/myitems",
            minArgs=0,
            description="Show peer's listed items"
        )
        self.commands = commands
        self.required_fields = required_fields or []

    def execute(self, args: list[str], peer_sub=None, room=None, emit_func=None, lock=None, auction_items=None):
        seller_items = {}
        print("Hello inside execute my items command")

 
        with lock:
            seller_items = {
                item_name: item
                for item_name, item in auction_items.items()
                if getattr(item, "seller", None) == peer_sub
            }
 
        # Emit to the client's room (or sid)
        seller_items_dicts = {name: item.to_dict() for name, item in seller_items.items()}
        if emit_func:
            emit_func("my_listed_items", seller_items_dicts, room=room)




#{
#    'a': 
#        {
#            'seller': '82798d6dcd7d18c0da55a65a5dde21a1cebf5069b3c08237d035dabd7bbc2dcd', 
#            'buyer': '173125b670f3d2785f01dc72d69e004f7ea7ed0f9a5e626adf5921bc90c03098', 
#            'name': 'a', 
#            'description': 'item a', 
#            'listing_timestamp': '2025-11-16T13:16:37.715918+00:00', 
#            'closing_date': '2026-05-05T00:00:00+00:00',
#            'minimum_bid': 0, 
#            'highest_bid': 20.0, 
#            'biding_timestamp': ['2025-11-16T13:16:57.274593+00:00', '2025-11-16T13:19:29.517305+00:00']
#        }
#}
