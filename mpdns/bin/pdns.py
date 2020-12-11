import requests
import time
import json
from splunk.clilib import cli_common as cli


class resourceLimitExceeded(Exception):
    pass


class connectionError(Exception):
    pass


def value_format(field, value):
    if isinstance(value, int) and (value > 10 ** 10):
        return time.strftime("%Y.%m.%d %H:%M:%S %Z", time.localtime(value / 1000))
    return value


class PDNS(object):
    def __init__(self):
        cfg = cli.getConfStanza("pdns", "config")
        self.api_url = cfg.get("api_url")
        self.api_key = cfg.get("api_key")
        self.proxy = cfg.get("proxy")

    def pdns_batch(self, value, limit):
        """
        Execute query until we have all results
        Limit is the total numer of results we want to recieve
        """
        result_list = []
        offset = 0
        size = 25  # Page size
        count = 0
        last = False

        parameters = {"limit": size}
        headers = {"Argus-API-Key": self.api_key} if self.api_key else None
        proxies = {"http": self.proxy, "https": self.proxy} if self.proxy else None

        while (not last) and (offset < limit):

            if offset + size > limit:
                parameters["limit"] = limit - offset

            parameters["offset"] = offset

            res = requests.get(
                f"{self.api_url}/pdns/v3/{value}", json=parameters, proxies=proxies
            )

            if res.status_code == 402:
                text = "Resource limit towards API exceeded. "
                if not self.api_key:
                    text += "Request for an API key to get a larger quota."
                else:
                    text += "Request a larger quota for your API key."
                raise resourceLimitExceeded(text)

            elif res.status_code != 200:
                raise connectionError(
                    f"Unable to connect to API. Make sure api_host ({self.api_url}) and " +
                    f"proxy ({self.proxy}) is correct. Error: {res.content}"
                    )

            result = res.json()

            count = result.get("count", 0)
            if count == 0:
                last = True

            for row in result["data"]:
                if "customer" in row and isinstance(row["customer"], dict):
                    row["customer"] = row["customer"]["shortName"]

                result_list.append(row)

            # result_list += data
            offset += len(result["data"])

            if offset >= count or offset >= limit:
                last = True

        return result_list

    def query(self, value, limit=100):
        result = self.pdns_batch(value, limit=limit)

        filtered = []

        for entry in result:
            filtered.append({k: value_format(k, v) for k, v in entry.items() if v})

        return filtered
