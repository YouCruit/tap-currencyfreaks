"""REST client handling, including CurrencyFreaksStream base class."""

import requests
from pathlib import Path
import logging
from typing import Any, Dict, Optional, Union, List, Iterable

from memoization import cached

from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.streams import RESTStream
from singer_sdk.authenticators import APIKeyAuthenticator

from dateutil.parser import parse as parse_datetime
import math


SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class CurrencyFreaksStream(RESTStream):
    """CurrencyFreaks stream class."""
    _LOG_REQUEST_METRICS: bool = False

    url_base = "https://api.currencyfreaks.com"
    records_jsonpath = "$."

    # OR use a dynamic url_base:
    # @property
    # def url_base(self) -> str:
    #     """Return the API URL root, configurable via tap settings."""
    #     return self.config["api_url"]

    next_page_token_jsonpath = "$.next_page"  # Or override `get_next_page_token`.

    @property
    def authenticator(self) -> APIKeyAuthenticator:
        """Return a new authenticator object."""
        return APIKeyAuthenticator.create_for_stream(
            self,
            key="apikey",
            value=self.config.get("api_key"),
            location="params"
        )

    @property
    def http_headers(self) -> dict:
        """Return the http headers needed."""
        headers = {}
        if "user_agent" in self.config:
            headers["User-Agent"] = self.config.get("user_agent")
        # If not using an authenticator, you may also provide inline auth headers:
        # headers["Private-Token"] = self.config.get("auth_token")
        return headers

    def get_next_page_token(
        self, response: requests.Response, previous_token: Optional[Any]
    ) -> Optional[Any]:
        """Return a token for identifying next page or None if no more pages."""
        return None

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {}
        # if next_page_token:
        #     params["page"] = next_page_token
        # if self.replication_key:
        #     params["sort"] = "asc"
        #     params["order_by"] = self.replication_key
        if self.config.get("symbols", []):
            params["symbols"] = ",".join(self.config["symbols"])
        return params

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        return [response.json()]

    def post_process(self, row: dict, context: Optional[dict] = None) -> Optional[dict]:
        """As needed, append or transform raw data to match expected structure."""
        parsed_date = parse_datetime(row['date'])
        # Fake ID: just the timestamp
        row['id'] = f"{math.floor(parsed_date.timestamp())}"
        # And fix type of date to parsed
        row['date'] = parsed_date
        return row
