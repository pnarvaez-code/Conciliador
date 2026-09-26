import json

def render(results):
    return json.dumps([x.to_dict() if hasattr(x, "to_dict") else x
                       for x in results], ensure_ascii=False, indent=2, default=str)

def resumen(results):
    values = list(results)
    def status(value):
        return value.status if hasattr(value, "status") else value.get("status")
    return {"total": len(values),
            "matched": sum(status(x) == "matched" for x in values)}
