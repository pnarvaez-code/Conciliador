import csv
import json

def _dict(item):
    return item.to_dict() if hasattr(item, "to_dict") else dict(item)

def a_json(items, *, indent=None):
    return json.dumps([_dict(item) for item in items], ensure_ascii=False,
                      indent=indent, default=str)

def a_csv(items):
    rows = [_dict(item) for item in items]
    if not rows:
        return ""
    import io
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=list(rows[0]), extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()

exportar_json = a_json
exportar_csv = a_csv
