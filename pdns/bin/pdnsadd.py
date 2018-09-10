import traceback
from splunk import Intersplunk

import pdns

def main():
    p = pdns.PDNS()

    # Parse arguments from splunk search
    opts, kwargs = Intersplunk.getKeywordsAndOptions()
    limit = int(kwargs.get("limit", 25))

    events, _, _ = Intersplunk.getOrganizedResults()


    # Annotate events
    for event in events:
        value = []
        for field in opts:
            if event.get(field):
                value.append(event[field])

        if not value:
            continue

        query = {}
        answer = {}
        for val in value:
            for res in p.query(val, limit=limit):
                if res["query"] != value:
                    query[res["query"]] = True
                if res["answer"] != value:
                    answer[res["answer"]] = True

        if query:
            if "query" not in event:
                event["query"] = query.keys()

        if answer:
            if "answer" not in event:
                event["answer"] = answer.keys()

    Intersplunk.outputResults(events)

try:
    main()
except Exception as e:
    Intersplunk.parseError(traceback.format_exc())
