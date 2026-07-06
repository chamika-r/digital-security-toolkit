"""
Breach Checker Module
Checks if a password has appeared in any known data breach
using the HaveIBeenPwned (HIBP) Pwned Passwords k-anonymity API.

Privacy design: only the first 5 characters of the SHA-1 hash
are sent to the API. The full password never leaves your machine.
"""

import hashlib
import requests

HIBP_PWNED_URL = "https://api.pwnedpasswords.com/range/{prefix}"


def hash_password(password):
    """
    SHA-1 hash the password.
    Returns (full_hash, prefix, suffix).
    prefix = first 5 chars (sent to API)
    suffix = remaining chars (checked locally)
    """
    sha1   = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    return sha1, sha1[:5], sha1[5:]


def check_password(password):
    """
    Check if a password has appeared in known data breaches.
    Uses the HIBP Pwned Passwords k-anonymity API — free, no key needed.
    Returns a dict with results.
    """
    if not password:
        return {
            'breached': False,
            'error':    'No password provided.',
            'count':    0,
            'hash_prefix': '',
        }

    full_hash, prefix, suffix = hash_password(password)

    try:
        response = requests.get(
            HIBP_PWNED_URL.format(prefix=prefix),
            headers={"User-Agent": "digital-security-toolkit-portfolio"},
            timeout=10
        )

        if response.status_code != 200:
            return {
                'breached':     None,
                'error':        f'API error: HTTP {response.status_code}',
                'count':        0,
                'hash_prefix':  prefix,
            }

        # Response is a list of SUFFIX:COUNT pairs
        # We check locally if our suffix appears — never sending full hash
        hashes = {}
        for line in response.text.splitlines():
            parts = line.split(':')
            if len(parts) == 2:
                hashes[parts[0]] = int(parts[1])

        count = hashes.get(suffix, 0)

        return {
            'breached':    count > 0,
            'error':       None,
            'count':       count,
            'hash_prefix': prefix,
        }

    except requests.exceptions.Timeout:
        return {
            'breached': None,
            'error':    'Request timed out — check your connection.',
            'count':    0,
            'hash_prefix': prefix,
        }
    except Exception as e:
        return {
            'breached': None,
            'error':    str(e),
            'count':    0,
            'hash_prefix': prefix,
        }