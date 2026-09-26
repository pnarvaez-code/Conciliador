import argparse, json
from .deterministic import sample_records
from .reconciliation import reconcile
from .http import serve

def main(argv=None):
    p = argparse.ArgumentParser(prog="conciliachain")
    sub = p.add_subparsers(dest="command")
    r = sub.add_parser("reconcile"); r.add_argument("--json", action="store_true")
    s = sub.add_parser("serve"); s.add_argument("--host", default="127.0.0.1"); s.add_argument("--port", type=int, default=8080)
    args = p.parse_args(argv)
    if args.command == "serve": return serve(args.host, args.port)
    left, right = sample_records(); result = [x.to_dict() for x in reconcile(left, right)]
    print(json.dumps(result, ensure_ascii=False) if getattr(args, "json", False) else "\n".join(f'{x["status"]}: {x["left_id"]} ({x["reason"]})' for x in result))

if __name__ == "__main__":
    main()
