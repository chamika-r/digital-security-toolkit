# Architecture

## Structure

digital-security-toolkit/
├── src/
│   ├── breach_checker.py    # HIBP k-anonymity password check
│   ├── metadata_stripper.py # EXIF read and strip via Pillow
│   └── app.py               # Flask web server
├── templates/
│   └── index.html           # Warm cream two-column dashboard
└── sample_images/           # Test images with EXIF data

## Data Flow

### Password breach check

User enters password
│
▼
SHA-1 hash computed locally
│
▼
First 5 chars sent to https://api.pwnedpasswords.com/range/{prefix}
│
▼
HIBP returns list of SUFFIX:COUNT pairs
│
▼
Check locally if full hash suffix appears → return count

### Image metadata strip

User uploads image
│
▼
metadata_stripper.read_metadata() → extract all EXIF tags
│
▼
Display fields with risk classification (HIGH/MEDIUM/LOW)
│
▼
metadata_stripper.strip_metadata() → paste pixels into new image
│
▼
Return clean image bytes as base64 for browser download

## Risk Classification

| Risk   | Tags |
|--------|------|
| HIGH   | GPSInfo, GPS coordinates, altitude, timestamp |
| MEDIUM | DateTime, Make, Model, Software, Artist, Copyright |
| LOW    | Resolution, Orientation, YCbCr settings, etc. |