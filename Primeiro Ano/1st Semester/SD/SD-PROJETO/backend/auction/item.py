from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

@dataclass
class Item:
    seller: str
    buyer: str
    name: str
    description: str
    listing_timestamp: datetime
    closing_date: datetime
    minimum_bid: float
    highest_bid: float
    biding_timestamp: list[datetime] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid4()))


    def __post_init__(self) -> None:
        if self.closing_date < self.listing_timestamp:
            raise ValueError("Closing date cannot be earlier than the listing_timestamp.")
        if self.minimum_bid < 0:
            raise ValueError("Minimum Bid cannot be negative.")
        if self.highest_bid < 0:
            raise ValueError("Highest Bid cannot be negative.")


    def get_id(self):
        return self.id

    

    def get_seller(self):
        return self.seller
    
    
    def get_buyer(self):
        return self.buyer


    def get_name(self):
        return self.name


    def get_description(self):
        return self.description
    

    def get_listing_timestamp(self):
        return self.listing_timestamp
    

    def get_biding_timestamp(self):
        return self.biding_timestamp
    

    def add_biding_timestamp(self, timestamp: datetime) -> list[datetime]:
        self.biding_timestamp.append(timestamp)
        return self.biding_timestamp

    def get_closing_date(self):
        return self.closing_date
    

    def get_minimum_bid(self):
        return self.minimum_bid
    
    
    def get_highest_bid(self):
        return self.highest_bid
    

    def is_open(self) -> bool:
        return datetime.now() < self.closing_date
    

    def is_valid_bid(self, bid_value: float) -> bool:
        return bid_value >= self.highest_bid
    

    def get_last_bid_timestamp(self):
        if not self.biding_timestamp:
            return None
        return datetime.fromisoformat(self.biding_timestamp[-1])


    
    
    def to_dict(self):
        return {
            "seller": self.seller,
            "buyer": self.buyer,
            "name": self.name,
            "description": self.description,
            "listing_timestamp": self.listing_timestamp.isoformat(),
            "closing_date": self.closing_date.isoformat(),
            "minimum_bid": self.minimum_bid,
            "highest_bid": self.highest_bid,
            "biding_timestamp": [dt.format() for dt in self.biding_timestamp],
            "id": self.id,
        }