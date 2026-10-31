# The 24 Urenloop 2026 group tombola: technical details

This explains exactly how the 4 group prizes are drawn and how to check the result yourself. For the short version,
see [the plain explanation](README.md) (in Dutch).

> **The facts** (filled in before the draw)
>
> | | |
> |---|---|
> | Ticket list | [`tombola_tickets.csv`](https://github.com/FrederikClinckaert/24UL-2026-tombola/blob/main/tombola_tickets.csv), frozen on 29 October 2026 at 12:33 (Brussels time) |
> | SHA-256 of the ticket list | `528c6c5b092380e8de2a82df1fed84cb4030fcd5f0612fda9a46fa93867a3cb6` |
> | drand chain | quicknet, `52db9ba70e0cc0f6eaf7803dd07447a1f5477735fd3f661792ba94600c84e971` |
> | drand round | **[33609412](https://api.drand.sh/52db9ba70e0cc0f6eaf7803dd07447a1f5477735fd3f661792ba94600c84e971/public/33609412)**, published on **Monday 2 November 2026 at 16:00:00** Brussels time (15:00:00 UTC, unix time `1793631600`) |
> | Result | **[AFTER THE DRAW]**: the round's random value and the output of `tombola_draw.py` |
> | Draw script | [`tombola_draw.py`](https://github.com/FrederikClinckaert/24UL-2026-tombola/blob/main/tombola_draw.py) (Python 3.9+, standard library only) |
> | Repository | [github.com/FrederikClinckaert/24UL-2026-tombola](https://github.com/FrederikClinckaert/24UL-2026-tombola) |

## In one sentence

The winners are a fixed, public function of two inputs: the **ticket list** (frozen and published, with its
SHA-256) and the **random value of one drand round** (announced before it existed). The draw itself has no other
input, no hidden randomness and no state.

```
winners = draw(tombola_tickets.csv, randomness of drand round R)
```

## 1. The ticket list

`tombola_tickets.csv`: UTF-8, `\n` line endings, a header `group,points`, then one row per group with more than
0 points. CSV quoting follows Python's `csv` module (a name with a comma or quote gets quoted).

```
group,points
Group A,40
Group B,25
...
```

- **Points** are the group points from the dashboard's group leaderboard at the moment of freezing. Every lap scores
  points by the hour it started (Brussels time), plus a rain bonus. A group's score is its members' points added up.
- **Order:** most points first; equal points alphabetically (ignoring case and accents). The order matters, because
  tickets are numbered down the list. The order that counts is the one in the published file.
- **Fingerprint:** the SHA-256 of the file's bytes. Check it with:

  ```bash
  shasum -a 256 tombola_tickets.csv                    # macOS, Linux
  certutil -hashfile tombola_tickets.csv SHA256        # Windows
  ```

The file is frozen once, in the organisers' dashboard, and published here with its fingerprint before the drand
round comes out. The repository keeps it byte for byte (`.gitattributes` turns off line-ending conversion), so a
clone or download has the same SHA-256 on every operating system.
Changes to groups or points after freezing don't affect the draw. The dashboard does warn when the live points
differ from the frozen list.

## 2. The random value: drand

[drand](https://drand.love) is a public randomness beacon run by the League of Entropy, a group of independent
organisations (among them Cloudflare, universities and security companies). Each round's value comes from a
*threshold* BLS signature: the network can only produce it when enough independent members cooperate. No single
member can compute or predict it before its time, and once published it is the same for everyone and can't be
changed.

We use the **quicknet** chain:

| | |
|---|---|
| Chain hash | `52db9ba70e0cc0f6eaf7803dd07447a1f5477735fd3f661792ba94600c84e971` |
| Scheme | `bls-unchained-g1-rfc9380` |
| Period | 3 seconds |
| Genesis (round 1) | unix time `1692803367` (2023-08-23 15:09:27 UTC) |
| Round `r` published at | `1692803367 + (r − 1) × 3` (unix time) |

A round is fetched from any relay; all serve the same signed data:

```
https://api.drand.sh/52db9ba70e0cc0f6eaf7803dd07447a1f5477735fd3f661792ba94600c84e971/public/<round>
```

Other relays: `api2.drand.sh`, `api3.drand.sh` and `drand.cloudflare.com`. Before the round's time, a relay answers
`HTTP 425 Too Early`. Afterwards it answers:

```json
{"round": 33489233,
 "randomness": "d0a49b420b7c684103408815cf98b3ba2ebf73747cb0f99cce2dec490bfb506a",
 "signature": "ac77b9b7ba1b3090b7858c51c0576b6cea3cbad6907ce83bcc87a3bcfb3dff921d62c1a345dd4001a7e08e4af28f3a13"}
```

`randomness` is the SHA-256 of `signature`. The signature itself verifies against the chain's public key (at
`/info` on any relay); drand's own client libraries do that check. `tombola_draw.py` checks that
`randomness = SHA-256(signature)` and that every relay it reaches returns the same value.

## 3. From the random value to the winners

Exactly what `draw()` in `tombola_draw.py` does:

```
left = the ticket list's groups, in file order
for prize k = 1, 2, 3, 4 (or fewer if fewer groups are left):
    N      = total points of the groups in `left`            # the tickets in the draw
    h      = SHA-256 of the ASCII text  "<randomness>:<k>"   # randomness: 64 lowercase hex characters
    x      = h read as an unsigned 256-bit big-endian integer
    ticket = (x mod N) + 1                                   # a ticket number from 1 to N
    number the tickets 1..N down `left`: a group holding p tickets after s earlier tickets has s+1 .. s+p
    the group holding `ticket` wins prize k and is removed from `left`
```

In Python (the actual code):

```python
pot = sum(points for _, points in left)
number = int.from_bytes(hashlib.sha256(f"{randomness}:{place}".encode("ascii")).digest(), "big")
ticket = number % pot + 1
```

**Why this gives every ticket the same chance.** SHA-256 output is, as far as anyone knows, indistinguishable from
uniform random bits, and its input contains the drand value, which nobody could know in advance. So `x` is uniform
on `[0, 2^256)`, and `x mod N` is uniform on `[0, N)` up to a deviation of at most `N / 2^256`, around 10⁻⁷⁴ here.
So a group holding `p` of the `N` tickets left wins prize `k` with probability `p / N`.

**One draw per prize.** Adding `:1`, `:2`, `:3`, `:4` gives four unrelated numbers from one drand value.

**A group wins once.** The winner leaves `left`, `N` shrinks by its points and the remaining groups are numbered
again, so their chances for the next prize go up.

### Worked example

This uses a **made-up** ticket list (not the real groups) and the real drand round 33489233, so you can reproduce it:

```
group,points
Group A,40
Group B,25
Group C,20
Group D,10
Group E,5
```

Round 33489233's randomness is `d0a49b420b7c684103408815cf98b3ba2ebf73747cb0f99cce2dec490bfb506a`.

| Prize | Tickets in the draw | SHA-256("randomness:k") starts with | Ticket | Ranges | Winner |
|---|---|---|---|---|---|
| 1 | 100 | `28137799dfcdacf8…` | 31 | A 1–40, B 41–65, C 66–85, D 86–95, E 96–100 | Group A |
| 2 | 60 | `9e560647cef04668…` | 38 | B 1–25, C 26–45, D 46–55, E 56–60 | Group C |
| 3 | 40 | `d85fe43c64c636f0…` | 39 | B 1–25, D 26–35, E 36–40 | Group E |
| 4 | 35 | `e293391da2e0060b…` | 11 | B 1–25, D 26–35 | Group B |

Group E won 3rd prize with only 5 tickets (a 12.5% chance at that point): small groups really can win.

## 4. How to check the real draw

**With the script** (Python 3.9 or newer, nothing to install):

```bash
git clone https://github.com/FrederikClinckaert/24UL-2026-tombola
cd 24UL-2026-tombola
python3 tombola_draw.py tombola_tickets.csv 33609412
```

(Or download the repository as a ZIP from GitHub.)

It prints the file's SHA-256 (compare it with the published one), fetches the round from all relays and checks that
they agree, then lists every prize: the tickets in the draw, each group's ticket range, the winning ticket and the
winner. Without internet, or if your Python can't verify HTTPS certificates, copy the `randomness` from the relay URL
in a browser:

```bash
python3 tombola_draw.py tombola_tickets.csv --randomness <randomness>
```

**By hand, without the script.** The hash for prize 1 with any SHA-256 tool:

```bash
printf '%s' '<randomness>:1' | shasum -a 256
```

Then `ticket = int(<hash>, 16) % N + 1` with `N` the total of the ticket list, for example in Python:
`python3 -c "print(int('<hash>', 16) % N + 1)"`. Find the group holding that ticket, remove it, and repeat for
prize 2 with `:2` and the new total.

You don't need to trust the dashboard: it only shows the result of this function. If it ever showed something else,
the check above would show it. (The organisers' dashboard runs an identical copy of this `tombola_draw.py`.)

## 5. The protocol

1. **Before the draw:** the points are final. The ticket list is frozen in the dashboard, and the following are
   published together: `tombola_tickets.csv`, its SHA-256, `tombola_draw.py`, these documents, and the drand round
   with its time. All of this happens **before that round is published**.
2. **At the ceremony:** after the round's time, the dashboard's first spin fetches the round from a drand relay.
   The prizes are revealed one by one: the wheel spins and stops on the winning ticket. The screen shows only the
   wheel and the winners. The fingerprint, the random value and every prize's ticket ranges and chances are in a
   collapsed panel of the dashboard.
3. **Afterwards:** the random value and the full output of `tombola_draw.py` are published here, and anyone can
   check it (see section 4).

## 6. What the organisers can and can't do

| Attempt | Why it fails |
|---|---|
| Change points or groups after publishing the list | The SHA-256 changes. The dashboard also draws from the frozen file, not the live points. |
| Pick a favourable drand round | The round was announced before its value existed. Only that round counts. |
| Try several rounds, or redraw | The result is fully determined by the list and the round. "Hide the places again" in the dashboard only replays the same result. |
| Show a different result on screen | Anyone running the check gets the real winners. |
| Hold the draw back until a good moment | Nothing to gain: the winners are fixed the moment the round comes out. |
| Influence drand | That needs a threshold of independent League of Entropy members to collude. |

**The one condition to check yourself:** the ticket list (with its SHA-256) and the round number must have been
published before the round's time. Compare the timestamp of the announcement (for example in the group chat) with
the round time in "The facts". Git commit dates don't prove this, because whoever commits can set them.

## 7. Practice runs

The dashboard has a *Practice* mode that uses drand's latest round. It's marked "Practice" on screen, it's kept
only in that browser, and it never affects the official draw, which depends only on the announced round.
