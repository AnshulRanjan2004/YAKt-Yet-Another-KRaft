
import threading
import time
from flask import Flask, jsonify, request
from pyraft import raft
import telnetlib
import json
import base64
from datetime import datetime
import random
import string

app = Flask(__name__)

stop_event = threading.Event()

node = None


def daemon_function():
    global node
    node = raft.make_default_node()
    node.start()

    while not stop_event.is_set():
        time.sleep(1)

    node.join()


daemon_thread = threading.Thread(target=daemon_function)
daemon_thread.start()


while node is None or node.ip is None or node.port is None:
    time.sleep(0.1)


'''
http endpoints below
'''


# test route
@app.route('/get_node_info', methods=['GET'])
def get_node_info():
    node_info = {
        "nid": node.nid,
        "ip": node.ip,
        "port": node.port,
    }

    return jsonify(node_info)


###############################################################################################################################
'''CRD API'''
###############################################################################################################################



def send_command(tn, command):
    tn.write(command.encode())
    return tn.read_until(b'\n', timeout=5).decode().strip()


def set_value(tn, key, value):
    # Encode the value as base64
    encoded_value = base64.b64encode(json.dumps(value).encode()).decode()

    # Set the key-value pair with the RESP command
    set_command = f'set {key} {encoded_value}\r\n'
    response = send_command(tn, set_command)
    print(response)


def del_value(tn, key):
    # Delete the key-value pair with the RESP command
    del_command = f'del {key}\r\n'
    response = send_command(tn, del_command)
    print(response)


def is_leader(node):
    return node.state == 'l'

'''


BrokerRecords


'''

def is_duplicate_broker(broker_id):
    for key, value in node.data.items():
        if key.startswith('RegisterBrokerRecord:'):
            try:
                decoded_value = base64.b64decode(value).decode()
                record = json.loads(decoded_value)

                if 'fields' in record and 'brokerId' in record['fields'] and record['fields']['brokerId'] == broker_id:
                    return True

            except (TypeError, json.JSONDecodeError):
                # Handle decoding errors or records without expected fields
                continue

    return False




def register_broker(data):
	if not is_leader(node):
		return jsonify({'error': 'Node is not the leader. Cannot write to metadata.'}), 400
	if 'name' in data and data['name'] == 'RegisterBrokerRecord':
		if is_duplicate_broker(data['fields']['brokerId']):
			return jsonify({'error': 'brokerId already exists'}), 400
		if(data['fields']['internalUUID']==''):
			data['fields']['internalUUID'] = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
		broker_uuid = data['fields']['internalUUID']
		key = f'RegisterBrokerRecord:{broker_uuid}'

		if(data['fields']['brokerStatus']==''):
			data['fields']['brokerStatus'] = 'ALIVE'
	
	
        	# Open a telnet connection to the node's port on localhost
		with telnetlib.Telnet('localhost', node.port) as tn:
            	# Send the key-value pair over telnet
			set_value(tn, key, data)

        	# Return the brokerId as a JSON response
		return jsonify({'internalUUID': broker_uuid, 'brokerId': data['fields']['brokerId']})

	return jsonify({'error': 'Invalid request'}), 400


@app.route('/register_broker', methods=['POST'])
def register_broker_route():
    data = request.get_json()

    response = register_broker(data)

    return response


def get_active_brokers():
    active_brokers = []

    for key, value in node.data.items():
        if key.startswith('RegisterBrokerRecord:'):
            record = json.loads(base64.b64decode(value).decode())
            if record['fields']['brokerStatus'] == 'ALIVE':
                active_brokers.append(record['fields']['internalUUID'])

    return active_brokers


@app.route('/get_active_brokers', methods=['GET'])
def get_active_brokers_route():
    # Assuming 'node' is the PyRaft node instance
    active_brokers = get_active_brokers()
    return jsonify({'active_brokers_ids': active_brokers})


def get_broker_by_id(requested_broker_id):
    for key, value in node.data.items():
        if key.startswith('RegisterBrokerRecord:'):
            record = json.loads(base64.b64decode(value).decode())
            if record['fields']['internalUUID'] == requested_broker_id:
                return record

    return None


@app.route('/get_broker_by_id', methods=['POST'])
def get_broker_by_id_route():
    data = request.get_json()

    if 'internalUUID' not in data:
        return jsonify({"error": "Missing 'brokerId' in the request"}), 400

    requested_broker_id = data['internalUUID']

    # Assuming 'node' is the PyRaft node instance
    broker_record = get_broker_by_id(requested_broker_id)

    if broker_record:
        return jsonify(broker_record)
    else:
        return jsonify({"error": f"No broker found with brokerId {requested_broker_id}"}), 404


'''


TopicRecords


'''


def create_topic(data):
	if 'name' in data and data['name'] == 'TopicRecord':
		topic_name = data['fields']['name']
		key = f'TopicRecord:{topic_name}'

		# Check if the node is the leader
		if not is_leader(node):
		    return jsonify({'error': 'Node is not the leader. Cannot write to metadata.'}), 400

		data['fields']['topicUUID'] = ''.join(random.choices(string.ascii_letters + string.digits, k=20))            
		# Open a telnet connection to the node's port on localhost
		with telnetlib.Telnet('localhost', node.port) as tn:
		    # Send the key-value pair over telnet
		    set_value(tn, key, data)

		# Return the topic name as a JSON response
		return jsonify({'topic_name': topic_name})

	return jsonify({'error': 'Invalid request'}), 400


@app.route('/create_topic', methods=['POST'])
def create_topic_route():
    data = request.get_json()

    response = create_topic(data)

    return response


def get_topic_by_name(requested_topic_name):
    for key, value in node.data.items():
        if key.startswith('TopicRecord:'):
            record = json.loads(base64.b64decode(value).decode())
            if record['fields']['name'] == requested_topic_name:
                return record

    return None

# Assuming 'node' is the PyRaft node instance


@app.route('/get_topic_by_name', methods=['POST'])
def get_topic_by_name_route():
    data = request.get_json()

    if 'topic_name' not in data:
        return jsonify({"error": "Missing 'topic_name' in the request"}), 400

    requested_topic_name = data['topic_name']

    # Assuming 'node' is the PyRaft node instance
    topic_record = get_topic_by_name(requested_topic_name)

    if topic_record:
        return jsonify(topic_record)
    else:
        return jsonify({"error": f"No topic found with name {requested_topic_name}"}), 404


'''


PartitionRecords


'''


def get_partition_by_id(requested_partition_id):
    for key, value in node.data.items():
        if key.startswith('PartitionRecord:'):
            record = json.loads(base64.b64decode(value).decode())
            if record['fields']['partitionId'] == requested_partition_id:
                return record

    return None


def update_partition(partition_id, data):
    key = f'PartitionRecord:{partition_id}'
    if not is_leader(node):
        return jsonify({'error': 'Node is not the leader. Cannot write to metadata.'}), 400
    with telnetlib.Telnet('localhost', node.port) as tn:
        set_value(tn, key, data)
    return jsonify({'partitionId': partition_id})


def create_partition(data):
    if 'name' in data and data['name'] == 'PartitionRecord':
        partition_id = data['fields']['partitionId']
        key = f'PartitionRecord:{partition_id}'

        if not is_leader(node):
            return jsonify({'error': 'Node is not the leader. Cannot write to metadata.'}), 400

        with telnetlib.Telnet('localhost', node.port) as tn:
            set_value(tn, key, data)

        return jsonify({'partitionId': partition_id})

    return jsonify({'error': 'Invalid request'}), 400


@app.route('/create_partition', methods=['POST'])
def create_partition_route():
    data = request.get_json()

    response = create_partition(data)

    return response


@app.route('/remove_replica', methods=['POST'])
def remove_replica():
    data = request.get_json()

    if 'name' in data and data['name'] == 'PartitionRecord':
        partition_id = data['fields']['partitionId']
        replica_to_remove = data['fields']['removingReplicas']

        partition_data = get_partition_by_id(partition_id)
        partition_data['fields']['removingReplicas'].append(replica_to_remove)
        partition_data['fields']['partitionEpoch'] += 1

        return update_partition(partition_id, partition_data)

    return jsonify({'error': 'Invalid request'}), 400


@app.route('/add_replica', methods=['POST'])
def add_replica():
    data = request.get_json()

    if 'name' in data and data['name'] == 'PartitionRecord':
        partition_id = data['fields']['partitionId']
        replica_to_add = data['fields']['addingReplicas']

        partition_data = get_partition_by_id(partition_id)
        partition_data['fields']['addingReplicas'].append(replica_to_add)
        partition_data['fields']['partitionEpoch'] += 1

        return update_partition(partition_id, partition_data)

    return jsonify({'error': 'Invalid request'}), 400


'''

ProducerIdsRecord

'''

def producer_ids_record(data):
    if 'name' in data and data['name'] == 'ProducerIdsRecord':
        broker_uuid = data['fields']['brokerId']
        producer_id = data['fields']['producerId']

        if not is_leader(node):
            return jsonify({'error': 'Node is not the leader. Cannot write to metadata.'}), 400
	
        record = get_broker_by_id(broker_uuid)
	
        if not record:
		#return jsonify({'error': 1})
            return jsonify({'error': f'No broker found with brokerId {broker_uuid}'}), 404
        #for key, value in node.data.items():
            #if broker_uuid in key:
                #record = json.loads(base64.b64decode(value).decode())
        data['fields']['brokerEpoch'] = record['fields']['epoch']

                # Check if brokerStatus is CLOSED
        if record['fields']['brokerStatus'] == 'CLOSED':
                    #print(f'Error: Cannot process request. Broker with ID {broker_uuid} is CLOSED. Producer registration is not allowed.')
            return jsonify({'error': 'Broker is CLOSED. Producer registration is not allowed.'}), 403

                #break

        key = f'ProducerIdsRecord:{producer_id}'
        with telnetlib.Telnet('localhost', node.port) as tn:
            set_value(tn, key, data)

        return jsonify({'producerId': producer_id, 'brokerUUId': broker_uuid})

    return jsonify({'error': 'Invalid request'}), 400


@app.route('/record_producer', methods=['POST'])
def record_producer_route():

    data = request.get_json()

    response = producer_ids_record(data)

    return response


'''


BrokerRegistrationChangeBrokerRecord


'''


def register_broker_change(data):
	if 'name' in data and data['name'] == 'RegistrationChangeBrokerRecord':
		broker_id = data['fields']['brokerId']

		# Check if the node is the leader
		if not is_leader(node):
		    return jsonify({'error': 'Node is not the leader. Cannot write to metadata.'}), 400

		# Fetch existing record
		existing_record = get_broker_by_id(broker_id)

		# Process the update logic here
		# ...
		if not existing_record:
		    #return jsonify({'error': 1})
		    return jsonify({'error': f'No broker found with brokerId {broker_id}'}), 404

		epochs = existing_record['fields']['epoch']
		existing_record['fields'].update(data['fields'])
		existing_record['name'] = 'RegisterBrokerRecord'
		existing_record['timestamp'] = data['timestamp']
		existing_record['fields']['epoch']  = str(int(epochs)+1)
		data['fields']['epoch'] = existing_record['fields']['epoch']

		register_broker(existing_record)
		unique_waow = data['timestamp']
		key = f'RegistrationChangeBrokerRecord:{unique_waow}'
		with telnetlib.Telnet('localhost', node.port) as tn:
		    set_value(tn, key, data)
		    
		return jsonify(existing_record)

	return jsonify({'error': 'Invalid request'}), 400


@app.route('/register_broker_change', methods=['POST'])
def register_broker_change_route():
    data = request.get_json()
    response = register_broker_change(data)
    return response


def unregister_broker(broker_id):
    existing_record = get_broker_by_id(broker_id)

    if existing_record:
        existing_record['fields']['brokerStatus'] = 'CLOSED'

        key = f'RegisterBrokerRecord:{broker_id}'
        with telnetlib.Telnet('localhost', node.port) as tn:
            set_value(tn, key, existing_record)

        return jsonify({'message': f'Broker with ID {broker_id} has been marked as CLOSED.'})

    # Return error if broker does not exist
    return jsonify({'error': f'No broker found with ID {broker_id}'}), 404



# Assuming 'node' is the PyRaft node instance
@app.route('/unregister_broker', methods=['DELETE'])
def unregister_broker_route():
    data = request.get_json()

    if 'brokerId' not in data:
        return jsonify({"error": "Missing 'brokerId' in the request"}), 400

    requested_broker_id = data['brokerId']
    response = unregister_broker(requested_broker_id)
    return response


'''


BrokerMgmt


'''

def get_latest_timestamp():
    latest_timestamp = 0

    for key, value in node.data.items():
        try:
            decoded_value = base64.b64decode(value).decode()
            record = json.loads(decoded_value)

            if 'timestamp' in record:
                latest_timestamp = max(latest_timestamp, int(record['timestamp']))

        except (TypeError, json.JSONDecodeError):
            # Handle decoding errors or records without a 'timestamp' field
            continue

    return latest_timestamp



def get_metadata_diff(previous_timestamp):
    metadata_diff = {}
    for key, value in node.data.items():
        try:
            decoded_value = base64.b64decode(value).decode()
            record = json.loads(decoded_value)
        except (TypeError, json.JSONDecodeError):
            # For 'ttl':{}
            continue

        record_timestamp = int(record['timestamp'])
        if record_timestamp > previous_timestamp:
            metadata_diff[key] = record

    return metadata_diff


def get_metadata_snapshot():
    metadata_snapshot = {}
    for key, value in node.data.items():
        try:
            decoded_value = base64.b64decode(value).decode()
            record = json.loads(decoded_value)
        except (TypeError, json.JSONDecodeError):
            # For 'ttl':{}
            continue

        metadata_snapshot[key] = record

    return metadata_snapshot


@app.route('/broker_mgmt', methods=['POST'])
def broker_mgmt():
    data = request.get_json()

    if 'timestamp' not in data:
        return jsonify({"error": "Missing 'timestamp' in the request"}), 400

    previous_timestamp = int(data['timestamp'])
    current_timestamp = get_latest_timestamp()

    time_difference_minutes = (current_timestamp - previous_timestamp) / 60

    if time_difference_minutes > 10:
        metadata_snapshot = get_metadata_snapshot()
        return jsonify(metadata_snapshot)

    metadata_diff = get_metadata_diff(previous_timestamp)
    return jsonify(metadata_diff)


'''


ClientMgmt


'''


@app.route('/client_mgmt', methods=['POST'])
def client_mgmt():
    data = request.get_json()

    if 'timestamp' not in data:
        return jsonify({"error": "Missing 'timestamp' in the request"}), 400

    previous_timestamp = int(data['timestamp'])
    current_timestamp = get_latest_timestamp()

    time_difference_minutes = (current_timestamp - previous_timestamp) / 60

    # required records for client_mgmt
    required_records = ['TopicRecord',
                        'PartitionRecord', 'RegisterBrokerRecord']

    if time_difference_minutes > 10:
        metadata_changes = get_metadata_snapshot()
        # return jsonify(metadata_snapshot)
    else:
        metadata_changes = get_metadata_diff(previous_timestamp)
    # return jsonify(metadata_diff)

    # filter out the required records
    required_records_data = {}
    for key, value in metadata_changes.items():
        if value['name'] in required_records:
            required_records_data[key] = value

    return jsonify(required_records_data)




app.run(host=node.ip, port=node.port+2)


