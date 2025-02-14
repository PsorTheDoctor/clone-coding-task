from flask import Flask, request, jsonify
import argparse
import statistics
import logging

from uart import is_running, messages, ser

app = Flask(__name__)

ap = argparse.ArgumentParser()
ap.add_argument('--host', type=str, default='localhost', help='Server host')
ap.add_argument('--port', type=int, default=7100, help='Server port')
ap.add_argument('--database_path', type=str, default='database.db', help='Database path')
args = ap.parse_args()

current_config = {'frequency': 1, 'debug': False}


@app.route('/start', methods=['GET'])
def start_device():
    global is_running
    if is_running:
        return jsonify({'error': 'Already running'}), 400
    is_running = True
    if ser:
        ser.write(b'$0\n')
        logging.info('Sent start command.')
    return jsonify({'status': 'started'}), 200


@app.route('/stop', methods=['GET'])
def stop_device():
    global is_running
    if not is_running:
        return jsonify({'error': 'Already stopped'}), 400
    is_running = False
    if ser:
        ser.write(b'$1\n')
        logging.info('Sent stop command.')
    return jsonify({'status': 'stopped'}), 200


@app.route('/configure', methods=['PUT'])
def config_device():
    global current_config
    data = request.json
    frequency = data.get('frequency')
    debug_flag = data.get('debug')
    if frequency is None or debug_flag is None:
        logging.error('Configuration request failed. Missing parameters.')
        return jsonify({'error': 'Missing parameters'}), 400

    current_config['frequency'] = frequency
    current_config['debug'] = debug_flag
    if ser:
        command = f'$2,{frequency}, {int(debug_flag)}\n'
        ser.write(command.encode('utf-8'))
        logging.info('Sent configuration command: %s', command)

    return jsonify({'status': 'configured', 'frequency': frequency, 'debug': debug_flag}), 200


@app.route('/messages', methods=['GET'])
def get_messages():
    limit = request.args.get('limit', default=10, type=int)
    logging.debug('Fetching last %d messages', limit)
    return jsonify(messages[-limit:]), 200


@app.route('/device', methods=['GET'])
def get_device_metadata():
    last_ten = messages[-10:]
    mean_last_ten = {
        'pressure': statistics.mean([msg['pressure'] for msg in last_ten]) if last_ten else 0,
        'temperature': statistics.mean([msg['temperature'] for msg in last_ten]) if last_ten else 0,
        'velocity': statistics.mean([msg['velocity'] for msg in last_ten]) if last_ten else 0,
    }
    latest = messages[-1] if messages else {'pressure': 0, 'temperature': 0, 'velocity': 0}

    logging.debug('Device metadata requested.')
    return jsonify({
        'debug': current_config['debug'],
        'curr_config': current_config,
        'mean_last_10': mean_last_ten,
        'latest': latest
    }), 200


if __name__ == '__main__':
    logging.info('Starting HTTP server %s:%d', args.host, args.port)
    app.run(host=args.host, port=args.port, debug=True)
