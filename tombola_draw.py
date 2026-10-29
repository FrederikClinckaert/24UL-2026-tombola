"""The group tombola's draw, exactly as the dashboard does it. Stand-alone: Python 3.9 or newer, nothing to install.

Check the result yourself with the published ticket list and the announced drand round:

    python3 tombola_draw.py tombola_tickets.csv 33510000          # fetches that drand round, prints the winners
    python3 tombola_draw.py tombola_tickets.csv --randomness d0a4…  # the same with the random value typed in
    python3 tombola_draw.py --round-at "2026-11-05 21:00"          # the drand round that comes out then (Brussels)

The rule: every point is a ticket, numbered 1, 2, 3, … down the ticket list. For prize k, the SHA-256 hash of the
text "<random value>:<k>", read as one big number, modulo the number of tickets left, plus 1, is the winning ticket.
The group holding it wins and leaves the draw; the tickets of the groups left are numbered again for the next prize.
"""
import argparse
import csv
import hashlib
import io
import json
import math
import ssl
import sys
import urllib.request
from datetime import datetime, timezone

PRIZES = 4
# drand's "quicknet" chain (League of Entropy): a new random value every 3 seconds, round 1 at GENESIS.
CHAIN = "52db9ba70e0cc0f6eaf7803dd07447a1f5477735fd3f661792ba94600c84e971"
GENESIS = 1692803367  # unix time of round 1
PERIOD = 3  # seconds between rounds
RELAYS = ("https://api.drand.sh", "https://drand.cloudflare.com", "https://api2.drand.sh", "https://api3.drand.sh")


def read_tickets(raw: bytes) -> list[tuple[str, int]]:
    """(group, points) in the order of the ticket list, from its CSV (columns group,points)."""
    return [(row["group"], int(row["points"])) for row in csv.DictReader(io.StringIO(raw.decode("utf-8")))]


def write_tickets(tickets: list[tuple[str, int]]) -> bytes:
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(["group", "points"])
    writer.writerows(tickets)
    return out.getvalue().encode("utf-8")


def fingerprint(raw: bytes) -> str:
    """SHA-256 of the ticket list file: what `shasum -a 256` (macOS, Linux) or `certutil -hashfile` (Windows) says."""
    return hashlib.sha256(raw).hexdigest()


def draw(tickets: list[tuple[str, int]], randomness: str, prizes: int = PRIZES) -> list[dict]:
    """The winners, 1st prize first: place, group, points, pot (tickets in the draw), ticket, and first/last, the
    winner's ticket numbers."""
    left = [(group, points) for group, points in tickets if points > 0]
    randomness = randomness.strip().lower()
    winners = []
    for place in range(1, min(prizes, len(left)) + 1):
        pot = sum(points for _, points in left)
        number = int.from_bytes(hashlib.sha256(f"{randomness}:{place}".encode("ascii")).digest(), "big")
        ticket = number % pot + 1
        first = 1
        for i, (group, points) in enumerate(left):
            if ticket < first + points:
                break
            first += points
        winners.append({"place": place, "group": group, "points": points, "pot": pot, "ticket": ticket,
                        "first": first, "last": first + points - 1})
        del left[i]
    return winners


def round_at(when: datetime) -> int:
    """The first drand round that comes out at or after this moment."""
    return max(1, math.ceil((when.timestamp() - GENESIS) / PERIOD) + 1)


def round_time(round_: int) -> datetime:
    """When this drand round comes out."""
    return datetime.fromtimestamp(GENESIS + (round_ - 1) * PERIOD, timezone.utc)


def fetch(round_: int, relay: str = RELAYS[0]) -> dict:
    """The round from one drand relay: {round, randomness, signature}. The random value is the SHA-256 of the
    signature, which is checked here. Raises when the round isn't out yet or the relay can't be reached."""
    request = urllib.request.Request(f"{relay}/{CHAIN}/public/{round_}", headers={"User-Agent": "tombola-draw"})
    with urllib.request.urlopen(request, timeout=10, context=_tls()) as response:
        beacon = json.load(response)
    if beacon["round"] != round_:
        raise ValueError(f"{relay} sent round {beacon['round']}, not {round_}")
    if hashlib.sha256(bytes.fromhex(beacon["signature"])).hexdigest() != beacon["randomness"]:
        raise ValueError(f"{relay}: the random value isn't the SHA-256 of the signature")
    return {key: beacon[key] for key in ("round", "randomness", "signature")}


def _tls() -> ssl.SSLContext:
    """HTTPS with certifi's certificates when it's installed: Python from python.org on macOS has none of its own."""
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


def _main() -> None:
    parser = argparse.ArgumentParser(description="Redo the group tombola's draw and print the winners.")
    parser.add_argument("tickets", nargs="?", help="the published ticket list (tombola_tickets.csv)")
    parser.add_argument("round", nargs="?", type=int, help="the announced drand round")
    parser.add_argument("--randomness", help="the round's random value, instead of fetching it")
    parser.add_argument("--round-at", metavar="'YYYY-MM-DD HH:MM'", help="print the round out then (Brussels time)")
    args = parser.parse_args()

    if args.round_at:
        from zoneinfo import ZoneInfo  # on Windows: pip install tzdata
        when = datetime.fromisoformat(args.round_at).replace(tzinfo=ZoneInfo("Europe/Brussels"))
        r = round_at(when)
        print(f"drand round {r} comes out at {round_time(r).astimezone(when.tzinfo):%Y-%m-%d %H:%M:%S} Brussels time")
        return
    if not args.tickets or not (args.round or args.randomness):
        parser.error("give the ticket list and the drand round (or --randomness)")

    with open(args.tickets, "rb") as f:
        raw = f.read()
    tickets = read_tickets(raw)
    print(f"Ticket list   {args.tickets}: {len(tickets)} groups, {sum(p for _, p in tickets)} tickets")
    print(f"Fingerprint   {fingerprint(raw)}  (compare it with the published one)")
    randomness = args.randomness
    if not randomness:
        seen = {}
        for relay in RELAYS:
            try:
                seen[relay] = fetch(args.round, relay)["randomness"]
            except Exception as e:  # one relay down is fine, as long as another one answers
                print(f"  ({relay}: {e})")
        if not seen:
            sys.exit(f"Couldn't get round {args.round}. It comes out at {round_time(args.round):%Y-%m-%d %H:%M:%S} "
                     f"UTC. If that has passed: with CERTIFICATE_VERIFY_FAILED above, run 'Install Certificates"
                     f".command' in your Python folder (macOS) or 'pip install certifi'; or open "
                     f"{RELAYS[0]}/{CHAIN}/public/{args.round} in a browser and pass its \"randomness\" with "
                     f"--randomness.")
        if len(set(seen.values())) > 1:
            sys.exit(f"The relays disagree on round {args.round}: {seen}")
        randomness = next(iter(seen.values()))
        print(f"drand round   {args.round}, out at {round_time(args.round):%Y-%m-%d %H:%M:%S} UTC "
              f"({len(seen)} relays agree)")
    print(f"Random value  {randomness.strip().lower()}")

    left = [(g, p) for g, p in tickets if p > 0]
    for w in draw(tickets, randomness):
        print(f"\nPrize {w['place']}: {w['pot']} tickets in the draw. "
              f"SHA-256('<random value>:{w['place']}') mod {w['pot']} + 1 = ticket {w['ticket']}")
        first = 1
        for g, p in left:
            print(f"  {first:>6}–{first + p - 1:<6} {g}{'   <-- wins' if g == w['group'] else ''}")
            first += p
        left = [(g, p) for g, p in left if g != w["group"]]
    print()


if __name__ == "__main__":
    _main()
