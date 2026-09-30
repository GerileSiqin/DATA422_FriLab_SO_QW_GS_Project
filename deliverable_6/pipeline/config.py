"""Name the analysis assumptions and expose portable run configuration."""

from dataclasses import dataclass
from pathlib import Path

LAYER_ID = 123515
CODE_FIELD = "SA22026_V1_00"
NAME_FIELD = "SA22026_V1_00_NAME"
ENDPOINT = "https://koordinates.com/services/query/v1/vector.json"
DAYS_PER_WEEK = 7
CENTRAL_SA2 = 326600


@dataclass(frozen=True)
class Config:
    """Input paths and explicit analysis settings for one run."""

    airbnb: Path
    bonds: Path
    cache: Path
    output: Path
    allow_network: bool = False
    workers: int = 8
    minimum_priced_listings: int = 5

    def validate(self) -> None:
        if not 1 <= self.workers <= 16:
            raise ValueError("workers must be between 1 and 16")
        if self.minimum_priced_listings < 1:
            raise ValueError("minimum_priced_listings must be positive")
        for path in (self.airbnb, self.bonds, self.cache):
            if not path.is_file():
                raise ValueError(f"Input file does not exist: {path}")
            # Outputs must never be allowed to replace an input file.
            if self.output.resolve() in path.resolve().parents:
                raise ValueError("Choose an output folder that does not contain inputs")
