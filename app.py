# backend/app.py
from db_utils import create_est_comp_trigger, update_est_comp_to_I, get_est_comp_logs
from flask import Flask, request, jsonify, send_from_directory
import os
from db_utils import activate_est_comp_to_A
from db_utils import make_backup, get_backup_list, delete_backup

app = Flask(__name__, static_folder='../frontend', static_url_path='')
BACKUP_DIR = './backups'

@app.route('/api/backups', methods=['GET'])
def list_backups():
    return jsonify(get_backup_list(BACKUP_DIR))

@app.route('/api/backups', methods=['POST'])
def create_backup():
    data = request.get_json()
    year = int(data['year'])
    month = int(data['month'])
    try:
        filename = make_backup(year, month, BACKUP_DIR)
        return jsonify({'filename': filename})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/backups/<filename>', methods=['DELETE'])
def remove_backup(filename):
    success = delete_backup(filename, BACKUP_DIR)
    if success:
        return jsonify({'status': 'deleted'})
    else:
        return jsonify({'error': 'no encontrado'}), 404

@app.route('/api/update_est_comp', methods=['POST'])
def update_est_comp():
    try:
        rows = update_est_comp_to_I()
        return jsonify({'updated': rows})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/logs', methods=['GET'])
def get_logs():
    try:
        logs = get_est_comp_logs()
        return jsonify(logs)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def root():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/ping')
def ping():
    return jsonify({'pong': True})

@app.route('/api/activate_est_comp', methods=['POST'])
def activate_est_comp():
    try:
        rows = activate_est_comp_to_A()
        return jsonify({'activated': rows})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

create_est_comp_trigger()

if __name__ == '__main__':
    os.makedirs(BACKUP_DIR, exist_ok=True)
    app.run(debug=True)
