"""
Metadata Stripper Module
Reads EXIF metadata from images and strips it to produce
a clean copy safe for sharing online.
"""

import io
from PIL import Image, ExifTags


HIGH_RISK_TAGS = {
    'GPSInfo', 'GPS', 'GPSLatitude', 'GPSLongitude',
    'GPSAltitude', 'GPSTimeStamp', 'GPSDateStamp',
}

MEDIUM_RISK_TAGS = {
    'DateTime', 'DateTimeOriginal', 'DateTimeDigitized',
    'Make', 'Model', 'Software', 'Artist', 'Copyright',
    'CameraOwnerName', 'BodySerialNumber', 'LensSerialNumber',
}


def _format_value(img, tag_id, tag_name, value):
    """Format an EXIF value for human-readable display."""
    if tag_name == 'GPSInfo':
        try:
            gps_data = img.getexif().get_ifd(tag_id)
            gps_tags = {
                ExifTags.GPSTAGS.get(k, str(k)): v
                for k, v in gps_data.items()
            }
            return str(gps_tags)[:200]
        except Exception:
            return 'GPS data present'
    elif isinstance(value, bytes):
        return f'<binary {len(value)} bytes>'
    elif isinstance(value, tuple):
        return str(value)[:100]
    else:
        return str(value)[:100]


def read_metadata(image_bytes):
    """
    Read all EXIF metadata from image bytes.
    Returns a dict with metadata fields and risk assessment.
    """
    try:
        img  = Image.open(io.BytesIO(image_bytes))
        exif = img.getexif()

        if not exif:
            return {
                'has_metadata': False,
                'fields':       [],
                'risk':         'NONE',
                'gps_found':    False,
                'field_count':  0,
                'format':       img.format,
                'size':         list(img.size),
            }

        fields    = []
        gps_found = False

        for tag_id, value in exif.items():
            tag_name = ExifTags.TAGS.get(tag_id, f'Unknown_{tag_id}')
            display  = _format_value(img, tag_id, tag_name, value)

            if tag_name in HIGH_RISK_TAGS or tag_name.startswith('GPS'):
                risk      = 'HIGH'
                gps_found = True
            elif tag_name in MEDIUM_RISK_TAGS:
                risk = 'MEDIUM'
            else:
                risk = 'LOW'

            fields.append({
                'tag_id':   tag_id,
                'tag_name': tag_name,
                'value':    display,
                'risk':     risk,
            })

        risk_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
        fields.sort(key=lambda x: risk_order.get(x['risk'], 3))

        if gps_found:
            overall_risk = 'HIGH'
        elif any(f['risk'] == 'MEDIUM' for f in fields):
            overall_risk = 'MEDIUM'
        elif fields:
            overall_risk = 'LOW'
        else:
            overall_risk = 'NONE'

        return {
            'has_metadata': True,
            'fields':       fields,
            'risk':         overall_risk,
            'gps_found':    gps_found,
            'field_count':  len(fields),
            'format':       img.format,
            'size':         list(img.size),
        }

    except Exception as e:
        return {
            'has_metadata': False,
            'fields':       [],
            'risk':         'NONE',
            'gps_found':    False,
            'field_count':  0,
            'error':        str(e),
        }


def strip_metadata(image_bytes, output_format=None):
    """
    Strip all EXIF metadata from an image.
    Returns clean image bytes with no metadata.
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        fmt = output_format or img.format or 'JPEG'

        if img.mode in ('RGBA', 'P'):
            clean = Image.new('RGBA', img.size)
            clean.paste(img)
        else:
            clean = Image.new(img.mode, img.size)
            clean.paste(img)

        output = io.BytesIO()
        clean.save(output, format=fmt, quality=95)
        output.seek(0)
        clean_bytes = output.read()

        return {
            'success':       True,
            'image_bytes':   clean_bytes,
            'format':        fmt,
            'original_size': len(image_bytes),
            'clean_size':    len(clean_bytes),
            'error':         None,
        }

    except Exception as e:
        return {
            'success':     False,
            'image_bytes': None,
            'error':       str(e),
        }