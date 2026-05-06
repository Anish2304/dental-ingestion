import json


def ingest_handler(records: list[dict]) -> str:
    output = json.dumps(records, indent=2)
    print(output)
    return output