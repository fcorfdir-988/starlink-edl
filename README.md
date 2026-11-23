# starlink-edl

Prefix lists for **Starlink (SpaceX)**, ready to be used as an *External Dynamic List* (EDL) on a firewall.
They are rebuilt every day from Starlink's official geofeed
(<https://geoip.starlinkisp.net/feed.csv>, RFC 8805).

| File | Content |
|---|---|
| `starlink-ipv4.txt` | aggregated IPv4 prefixes, one per line |
| `starlink-ipv6.txt` | aggregated IPv6 prefixes, one per line |

## How it works

- **Update:** a GitHub Actions workflow (`.github/workflows/update.yml`) runs every day at 03:17 UTC.
  A commit is created only when the content changes.
- **Safeguards:** if the feed cannot be downloaded, looks truncated (fewer than 1,000 lines per
  address family) or would exceed 50,000 entries (the capacity of a PAN-OS IP list), nothing is
  published and the previous files stay in place.
- **Manual run:** *Actions* tab > *update-starlink-edl* > *Run workflow*, or `python3 update.py`
  locally (Python 3, no dependencies).
- **Inactivity:** GitHub disables scheduled workflows after 60 days without repository activity.
  The workflow writes a `HEARTBEAT` file when there has been no commit for 45 days to prevent this.

## Usage on Palo Alto Networks firewalls

Objects > External Dynamic Lists > Add, type **IP List**:

- Source: `https://raw.githubusercontent.com/<account>/<repository>/main/starlink-ipv4.txt`
  (then the same for `starlink-ipv6.txt`)
- Certificate profile: a profile containing the root CA that signs the certificate of
  `raw.githubusercontent.com`
- Repeat: *Daily* (or *Hourly*)

An EDL is only downloaded once a policy rule references it.

## Notes

- The data is public and comes from Starlink itself. It is not authoritative for IP ownership and
  can change without notice, which is why the lists are refreshed daily.
- This repository contains no information specific to any user or organisation.
