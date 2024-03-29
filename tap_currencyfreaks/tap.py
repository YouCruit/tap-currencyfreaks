"""CurrencyFreaks tap class."""

from typing import List

from singer_sdk import Tap, Stream
from singer_sdk import typing as th  # JSON schema typing helpers
# Import your custom stream types here:
from tap_currencyfreaks.streams import (
    LatestStream,
)
# Compile a list of custom stream types here
# OR rewrite discover_streams() below with your custom logic.
STREAM_TYPES = [
    LatestStream,
]


class TapCurrencyFreaks(Tap):
    """CurrencyFreaks tap class."""
    name = "tap-currencyfreaks"

    # Update this section with the actual config values you expect:
    config_jsonschema = th.PropertiesList(
        th.Property(
            "api_key",
            th.StringType,
            required=True,
            description="The token to authenticate against the API service"
        ),
        th.Property(
            "symbols",
            th.ArrayType(th.StringType),
            required=False,
            description="Specify currencies to fetch; If none all currencies will be fetched"
        ),
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]
