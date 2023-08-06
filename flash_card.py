import json


class FlashCard:
    def __init__(self, frontside: str, backside: str):
        self.frontside = frontside
        self.backside = backside

    def __str__(self):
        return json.dumps(self, indent=4, default=vars)

    def as_csv(self) -> str:
        return self.frontside + ';' + self.backside