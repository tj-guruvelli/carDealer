#!/usr/bin/env python3
"""Check that every wired car-data API is reachable and its key is valid.

Prints a pass/fail line per service. Never prints a key or a raw response body —
CarsXE echoes the API key back inside its JSON, so raw bodies are unsafe to log.
Only explicitly named fields are extracted.

Usage:
    python health_check.py
    python health_check.py --json
    python health_check.py --service carvector

Exit code 0 if every configured service passes, 1 otherwise. Services whose key is
not set are reported as SKIP and do not fail the run.

Stdlib only.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

TIMEOUT_SECONDS = 30

# A probe is a cheap, known-good request whose answer we can recognize.
# `pick` pulls only named fields out of the parsed JSON. Never echo the whole body.
SERVICES = {
    "carvector": {
        "env": "CARVECTOR_API_KEY",
        "url": "https://api.carvector.io/v1/dtc/P0404",
        "auth": ("header", "Authorization", "Bearer {key}"),
        "pick": lambda d: "{} {}".format(d.get("code"), d.get("title")),
    },
    "cardog": {
        "env": "CARDOG_API_KEY",
        "url": "https://api.cardog.app/v2/vin/5YJ3E1EA8PF000001",
        "auth": ("header", "x-api-key", "{key}"),
        "pick": lambda d: "{} {} {}".format(d.get("year"), d.get("make"), d.get("model")),
    },
    "carsxe": {
        "env": "CARSXE_API_KEY",
        "url": "https://api.carsxe.com/specs?vin=1HGCM82633A004352&key={key}",
        "auth": ("query", None, None),
        "pick": lambda d: "{} {} {}".format(
            d.get("attributes", {}).get("year"),
            d.get("attributes", {}).get("make"),
            d.get("attributes", {}).get("model"),
        ),
    },
    "marketcheck": {
        "env": "MARKETCHECK_API_KEY",
        "url": (
            "https://api.marketcheck.com/v2/search/car/active"
            "?make=Cadillac&model=CTS&rows=1&api_key={key}"
        ),
        "auth": ("query", None, None),
        "pick": lambda d: "num_found={}".format(d.get("num_found")),
    },
}


def redact(text, secrets):
    """Replace any secret appearing in text with a masked marker.

    Defence in depth: even though probes extract named fields, an error message
    can still contain the URL, and CarsXE puts the key in the query string.
    """
    result = text
    for secret in secrets:
        if secret and len(secret) >= 8:
            result = result.replace(secret, "***REDACTED***")
    return result


def probe(name, config, key):
    """Make one request and return (status, detail). Never returns a raw body."""
    url = config["url"].format(key=key)
    kind, header_name, header_template = config["auth"]
    request = urllib.request.Request(url)
    if kind == "header":
        request.add_header(header_name, header_template.format(key=key))

    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        hint = " (check the key)" if error.code in (401, 403) else ""
        return "FAIL", "HTTP {}{}".format(error.code, hint)
    except urllib.error.URLError as error:
        return "FAIL", redact("network: {}".format(error.reason), [key])
    except (ValueError, TimeoutError) as error:
        return "FAIL", redact("bad response: {}".format(error), [key])

    try:
        return "OK", redact(str(config["pick"](payload)), [key])
    except (KeyError, TypeError, AttributeError) as error:
        return "FAIL", "unexpected response shape: {}".format(type(error).__name__)


def run(selected=None, env=None):
    """Probe each service. Returns a list of {service, status, detail} dicts."""
    env = os.environ if env is None else env
    names = [selected] if selected else list(SERVICES)
    results = []
    for name in names:
        config = SERVICES[name]
        key = env.get(config["env"], "")
        if not key:
            results.append(
                {
                    "service": name,
                    "status": "SKIP",
                    "detail": "{} not set".format(config["env"]),
                }
            )
            continue
        status, detail = probe(name, config, key)
        results.append({"service": name, "status": status, "detail": detail})
    return results


def exit_code(results):
    """Fail only on real failures. A missing key is a SKIP, not an error."""
    return 1 if any(r["status"] == "FAIL" for r in results) else 0


def render(results):
    width = max(len(r["service"]) for r in results)
    return "\n".join(
        "%-*s  %-4s  %s" % (width, r["service"], r["status"], r["detail"]) for r in results
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--json", action="store_true", help="emit JSON instead of a table")
    parser.add_argument("--service", choices=sorted(SERVICES), help="probe just one service")
    args = parser.parse_args(argv)

    results = run(selected=args.service)
    print(json.dumps(results, indent=2) if args.json else render(results))
    return exit_code(results)


if __name__ == "__main__":
    sys.exit(main())
