# 🛡️ Digital Security Toolkit

Two privacy tools in one web app — built for anyone who cares about their digital security.

## Tools

### 1. Password Breach Checker
Check if a password has appeared in any known data breach using the [HaveIBeenPwned](https://haveibeenpwned.com) Pwned Passwords API.

**Privacy-first**: only the first 5 characters of a SHA-1 hash are sent to the API. Your password never leaves your device.

### 2. Image Metadata Stripper
Upload an image, see all hidden EXIF metadata (GPS location, device make/model, timestamps), then download a clean copy with everything removed.

Supports: JPG · PNG · TIFF · WebP · BMP

## Setup

```bash
git clone https://github.com/chamika-r/digital-security-toolkit.git
cd digital-security-toolkit
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
PYTHONPATH=. python3 src/app.py
```

Open `http://127.0.0.1:5003`

## How the breach checker works (k-anonymity)

1. SHA-1 hash the password locally
2. Send only the first 5 characters of the hash to HIBP
3. HIBP returns all hashes starting with those 5 characters
4. Check locally if the full hash appears in the results
5. The complete password and hash never leave your device

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)