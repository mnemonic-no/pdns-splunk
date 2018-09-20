import urllib2
import urllib
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
        cfg = cli.getConfStanza('pdns', 'config')
        api_url = cfg.get("api_url")
        api_key = cfg.get("api_key")
        proxy = cfg.get("proxy")

        if proxy:
            proxy_handler = urllib2.ProxyHandler({'http': proxy})
            opener = urllib2.build_opener(proxy_handler)
        else:
            opener = urllib2.build_opener()

        if api_key:
            opener.addheaders = [('Argus-API-Key', api_key)]

        self.opener = opener
        self.api_url = api_url
        self.api_key = api_key
        self.proxy = proxy

    def pdns_batch(self, value, limit):
        """
        Execute query until we have all results
        Limit is the total numer of results we want to recieve
        """
        result_list = []
        offset = 0
        size = 25 # Page size
        count = 0
        last = False

        parameters = {"limit": size}

        while (not last) and (offset < limit):

            if offset + size > limit:
                parameters["limit"] = (limit - offset)

            parameters["offset"] = offset

            try:
                result = json.loads(self.opener.open("{}/pdns/v3/{}?{}".format(
                    self.api_url,
                    value,
                    urllib.urlencode(parameters)
                )).read())
            except urllib2.URLError as e:
                if str(e) == "HTTP Error 402: Payment Required":
                    text = "Resource limit towards API exceeded. "
                    if not self.api_key:
                        text += "Request for an API key to get a larger quota."
                    else:
                        text += "Request a larger quota for your API key."
                    raise resourceLimitExceeded(text)

                raise connectionError("Unable to connect to API. Make sure api_host ({}) and proxy ({}) is correct. Error: {}".format(self.api_url, self.proxy, e))

            response_code = result["responseCode"]

            data = result["data"]
            count = result.get("count", 0)
            if count == 0:
                last = True

            result_list += data
            offset += len(data)

            if offset >= count or offset >= limit:
                last = True

        return result_list

    def query(self, value, limit = 100):
        result = self.pdns_batch(value, limit = limit)

        filtered = []

        for entry in result:
            filtered.append({k: value_format(k, v) for k, v in entry.items() if v})

        return filtered
