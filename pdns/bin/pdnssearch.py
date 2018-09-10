import traceback
from splunk import Intersplunk

import pdns

def main():
    p = pdns.PDNS()

    # Parse arguments from splunk search
    opts, kwargs = Intersplunk.getKeywordsAndOptions()

    # Get limit from kwargs, but default to 25 if not specified
    limit = int(kwargs.get("limit", 25))

    results = []

    for value in opts:
        try:
            result = p.query(value, limit = limit)
        except pdns.resourceLimitExceeded as e:
            Intersplunk.parseError(str(e))
            return

        results += result
    Intersplunk.outputResults(results)


try:
    main()
except Exception as e:
    Intersplunk.parseError(traceback.format_exc())
