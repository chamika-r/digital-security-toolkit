"""
Flask Web Application
Digital Security Toolkit — password breach checker and image metadata stripper.
"""

import os
import io
import base64
import tempfile
from flask import Flask, render_template, request, jsonify, send_file
from breach_checker import check_password
from metadata_stripper import read_metadata, strip_metadata

app = Flask(__name__, template_folder='../templates')
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/check-password', methods=['POST'])
def check_password_route():
    data     = request.get_json()
    password = data.get('password', '').strip()

    if not password:
        return jsonify({'error': 'No password provided'}), 400

    result = check_password(password)
    return jsonify(result)


@app.route('/read-metadata', methods=['POST'])
def read_metadata_route():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    allowed = {'.jpg', '.jpeg', '.png', '.tiff', '.webp', '.bmp'}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed:
        return jsonify({'error': f'Unsupported format. Allowed: {", ".join(allowed)}'}), 400

    image_bytes = file.read()
    result      = read_metadata(image_bytes)
    result['filename'] = file.filename
    return jsonify(result)


@app.route('/strip-metadata', methods=['POST'])
def strip_metadata_route():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    image_bytes = file.read()

    # Read metadata first so we can report what was removed
    meta   = read_metadata(image_bytes)
    result = strip_metadata(image_bytes)

    if not result['success']:
        return jsonify({'error': result['error']}), 500

    # Return clean image as base64 for download
    clean_b64 = base64.b64encode(result['image_bytes']).decode('utf-8')

    ext      = os.path.splitext(file.filename)[1].lower()
    fmt      = result['format'].lower()
    out_name = f"clean_{os.path.splitext(file.filename)[0]}.{fmt}"

    return jsonify({
        'success':           True,
        'filename':          file.filename,
        'output_filename':   out_name,
        'fields_removed':    meta['field_count'],
        'gps_removed':       meta['gps_found'],
        'original_size':     len(image_bytes),
        'clean_size':        len(result['image_bytes']),
        'image_b64':         clean_b64,
        'mime_type':         f'image/{fmt}',
    })


@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})


if __name__ == '__main__':
    app.run(debug=True, port=5003)