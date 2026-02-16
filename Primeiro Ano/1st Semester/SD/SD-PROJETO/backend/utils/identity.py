from dataclasses import dataclass
from mnemonic import Mnemonic


@dataclass(frozen=True)
class UserIdentity:

    mnemonic: str
    username: str = ""

    @classmethod
    def from_prompt(cls) -> "UserIdentity":
        mnemo = Mnemonic("english")
        choice = input("Do you already have a mnemonic? (y/n) ").strip().lower()
        if choice == "y":
            mnemonic = input("Enter your existing mnemonic: ").strip()
        else:
            mnemonic = mnemo.generate(strength=128)
            print("Save this mnemonic securely!")
            print(mnemonic)
        username  = input("Enter your username: ").strip()
        return cls(mnemonic=mnemonic, username=username)