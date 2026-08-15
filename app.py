from flask import Flask, render_template, request, jsonify, send_from_directory, session
import random
import os
import time
from datetime import datetime
from adb_helper import ADBHelper

app = Flask(__name__)
app.secret_key = os.urandom(24)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'downloads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

SESSIONS = {}
HISTORY = []

def generate_pin():
    return str(random.randint(100000, 999999))

@app.route('/')
def index():
    return render_template('base.html')

@app.route('/tv')
def tv_view():
    pin = generate_pin()
    SESSIONS[pin] = {
        'created_at': time.time(),
        'connected': False,
        'file_ready': None,
        'progress': 0,
        'status': 'بانتظار الاقتران...'
    }
    session['tv_pin'] = pin
    return render_template('tv.html', pin=pin)

@app.route('/phone')
def phone_view():
    return render_template('phone.html')

@app.route('/api/pair', methods=['POST'])
def pair():
    data = request.json or {}
    pin = data.get('pin')
    if pin in SESSIONS:
        SESSIONS[pin]['connected'] = True
        SESSIONS[pin]['status'] = 'تم الاتصال بالهاتف'
        return jsonify({'success': True, 'message': 'تم الاقتران بنجاح'})
    return jsonify({'success': False, 'message': 'رمز الاقتران غير صحيح'}), 400

@app.route('/api/status/<pin>')
def get_status(pin):
    if pin in SESSIONS:
        return jsonify(SESSIONS[pin])
    return jsonify({'error': 'الجلسة غير موجودة'}), 404

@app.route('/api/apps', methods=['GET'])
def list_apps():
    packages = ADBHelper.get_installed_packages()
    return jsonify({'packages': packages})

@app.route('/api/transfer', methods=['POST'])
def transfer_app():
    data = request.json or {}
    pin = data.get('pin')
    package_name = data.get('package_name')

    if pin not in SESSIONS or not SESSIONS[pin]['connected']:
        return jsonify({'success': False, 'message': 'غير مسموح أو الجلسة غير مقترنة'}), 403

    SESSIONS[pin]['status'] = f'جاري استخراج {package_name}...'
    file_path, err = ADBHelper.extract_package(package_name, UPLOAD_FOLDER)

    if err:
        SESSIONS[pin]['status'] = f'خطأ: {err}'
        HISTORY.append({
            'app': package_name, 'size': '0 MB',
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'status': 'فشل'
        })
        return jsonify({'success': False, 'message': err}), 500

    file_name = os.path.basename(file_path)
    file_size = round(os.path.getsize(file_path) / (1024 * 1024), 2)

    SESSIONS[pin]['file_ready'] = file_name
    SESSIONS[pin]['status'] = 'اكتمل النقل وجاهز للتنزيل'
    SESSIONS[pin]['progress'] = 100

    HISTORY.append({
        'app': package_name,
        'size': f'{file_size} MB',
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'status': 'نجاح'
    })

    return jsonify({'success': True, 'file_name': file_name, 'size_mb': file_size})

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

@app.route('/api/history')
def get_history():
    return jsonify(HISTORY)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
