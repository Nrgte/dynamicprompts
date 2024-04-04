from dataclasses import dataclass
from dynamicprompts.wildcards.collection.base import WildcardCollection

@dataclass(frozen=True)
class WildcardValue:
    value: str
    source: WildcardCollection