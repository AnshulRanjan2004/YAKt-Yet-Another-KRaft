import requests
from datetime import datetime

def send_request(port, endpoint, method='GET', payload=None):
    url = f'http://localhost:{port}/{endpoint}'

    try:
        if method == 'GET':
            #print("in get")
            response = requests.get(url, json=payload)
        elif method == 'POST':
            #print("in post")
            #print(url, payload)
            response = requests.post(url, json=payload)
        elif method == 'PUT':
            response = requests.put(url, json=payload)
        elif method == 'DELETE':
            response = requests.delete(url, json=payload)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        #response.raise_for_status()  # Check if the request was successful
        print(response.text)
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

# Example usage:
# send_request(5012, 'get_node_info')
# send_request(5012, 'your_endpoint', method='POST', payload={"key": "value"})



'''


BrokerRecords


'''




uuid2 = send_request(5012, 'register_broker', method='POST', payload={
    "type": "metadata",
    "name": "RegisterBrokerRecord",
    "fields": {
        "internalUUID": "",
        "brokerId": 0,
        "brokerHost": "",
        "brokerPort": "",
        "securityProtocol": "",
        "brokerStatus": "",
        "rackId": "",
        "epoch": 0
    },
    "timestamp": str(int(datetime.now().timestamp()))
}).json()['internalUUID']


uuid = send_request(5012, 'register_broker', method='POST', payload={
    "type": "metadata",
    "name": "RegisterBrokerRecord",
    "fields": {
        "internalUUID": "",
        "brokerId": 1,
        "brokerHost": "",
        "brokerPort": "",
        "securityProtocol": "",
        "brokerStatus": "",
        "rackId": "",
        "epoch": 0
    },
    "timestamp": str(int(datetime.now().timestamp()))
}).json()['internalUUID']


send_request(5012, 'register_broker', method='POST', payload={
    "type": "metadata",
    "name": "RegisterBrokerRecord",
    "fields": {
        "internalUUID": "",
        "brokerId": 1,
        "brokerHost": "",
        "brokerPort": "",
        "securityProtocol": "",
        "brokerStatus": "",
        "rackId": "",
        "epoch": 0
    },
    "timestamp": str(int(datetime.now().timestamp()))
})


send_request(5012, 'get_active_brokers', method='GET')

send_request(5012, 'get_broker_by_id', method='POST', payload = {"internalUUID": str(uuid)})




'''


TopicRecords


'''


send_request(5012, 'create_topic', method='POST', payload = {
	"type": "metadata",
	"name": "TopicRecord",
	"fields": {
		"topicUUID": "",
		"name": "Likes"
	},
	"timestamp": str(int(datetime.now().timestamp()))
})


send_request(5012, 'create_topic', method='POST', payload = {
	"type": "metadata",
	"name": "TopicRecord",
	"fields": {
		"topicUUID": "",
		"name": "Comments"
	},
	"timestamp": str(int(datetime.now().timestamp()))
})

send_request(5012, 'get_topic_by_name', method='POST', payload = {"topic_name": "Likes"})




'''


PartitionRecords


'''

# Create Partition
send_request(5012, 'create_partition', method='POST', payload={
    "type": "metadata",
    "name": "PartitionRecord",
    "fields": {
        "partitionId": 1,
        "topicUUID": "123456789",
        "replicas": [1, 2, 3],
        "ISR": [1, 2],
        "removingReplicas": [],
        "addingReplicas": [],
        "leader": "1",
        "partitionEpoch": 1
    },
    "timestamp": str(int(datetime.now().timestamp()))
})


send_request(5012, 'add_replica', method='POST', payload={
    "type": "metadata",
    "name": "PartitionRecord",
    "fields": {
        "partitionId": 1,
        "addingReplicas": 4
    },
    "timestamp": str(int(datetime.now().timestamp()))
})


send_request(5012, 'remove_replica', method='POST', payload={
    "type": "metadata",
    "name": "PartitionRecord",
    "fields": {
        "partitionId": 1,
        "removingReplicas": 3
    },
    "timestamp": str(int(datetime.now().timestamp()))
})



'''

    ProducerIdsRecord

'''

send_request(5012, 'record_producer', method='POST', payload={
    
	"type": "metadata",
	"name": "ProducerIdsRecord",
	"fields": {
		"brokerId": str(uuid), 
		"brokerEpoch": 0, 
		"producerId": 0 
	},
	"timestamp": str(int(datetime.now().timestamp())) 

})


'''


BrokerRegistrationChangeBrokerRecords


'''
send_request(5012, 'register_broker_change', method='POST', payload={
    "type": "metadata",
    "name": "RegistrationChangeBrokerRecord",
    "fields": {
        "brokerId": str(uuid),
        "brokerHost": "new_host",
        "brokerPort": "new_port",
        "securityProtocol": "new_protocol",
        "brokerStatus": "new_status",
        "epoch": 0
    },
    "timestamp": str(int(datetime.now().timestamp()))
})

send_request(5012, 'register_broker_change', method='POST', payload={
    "type": "metadata",
    "name": "RegistrationChangeBrokerRecord",
    "fields": {
        "brokerId": str(uuid)+'e',
        "brokerHost": "new_host",
        "brokerPort": "new_port",
        "securityProtocol": "new_protocol",
        "brokerStatus": "new_status",
        "epoch": 0
    },
    "timestamp": str(int(datetime.now().timestamp()))
})


send_request(5012, 'unregister_broker', method='DELETE' , payload = {"brokerId": str(uuid2)})

'''


BrokerMgmt


'''

    
timestamp_now = int(datetime.now().timestamp())
timestamp_before = timestamp_now - 800  #timestamp older than 10 minutes

send_request(5012, 'broker_mgmt', method='POST', payload = {"timestamp":str(timestamp_before)})

#Creating a new record, which should be returned as diff for a timestamp < 10 mins

send_request(5012, 'register_broker', method='POST', payload={
    "type": "metadata",
    "name": "RegisterBrokerRecord",
    "fields": {
        "internalUUID": "",
        "brokerId": 5,
        "brokerHost": "",
        "brokerPort": "",
        "securityProtocol": "",
        "brokerStatus": "",
        "rackId": "",
        "epoch": 0
    },
    "timestamp": str(timestamp_now+240)	#timestamp_now is 5 seconds older than the newly added record
})



send_request(5012, 'record_producer', method='POST', payload={
    
	"type": "metadata",
	"name": "ProducerIdsRecord",
	"fields": {
		"brokerId": str(uuid), # type : string; uuid of requesting broker
		"brokerEpoch": 0, # type : int; the epoch at which broker requested
		"producerId": 19 # type : int; producer id requested 
	},
	"timestamp": str(int(datetime.now().timestamp())+300) # type :  timestamp

})



send_request(5012, 'broker_mgmt', method='POST', payload = {"timestamp":str(timestamp_now)})


'''


Client Mgmt


'''

timestamp_now = int(datetime.now().timestamp())
timestamp_before = timestamp_now - 800  #timestamp older than 10 minutes

send_request(5012, 'client_mgmt', method='POST', payload = {"timestamp":str(timestamp_before)})

#Creating a new record, which should be returned as diff for a timestamp < 10 mins

# creating a broker record
send_request(5012, 'register_broker', method='POST', payload={
    "type": "metadata",
    "name": "RegisterBrokerRecord",
    "fields": {
        "internalUUID": "",
        "brokerId": 5,
        "brokerHost": "",
        "brokerPort": "",
        "securityProtocol": "",
        "brokerStatus": "",
        "rackId": "",
        "epoch": 0
    },
    "timestamp": str(timestamp_now+240)	#timestamp_now is 5 seconds older than the newly added record
})

# creating a topic record
send_request(5012, 'create_topic', method='POST', payload = {
    "type": "metadata",
    "name": "TopicRecord",
    "fields": {
        "topicUUID": "",
        "name": "Share"
    },
    "timestamp": str(timestamp_now+240)
})

# create a producer record
send_request(5012, 'record_producer', method='POST', payload={
    
    "type": "metadata",
    "name": "ProducerIdsRecord",
    "fields": {
        "brokerId": str(uuid), # type : string; uuid of requesting broker
        "brokerEpoch": 0, # type : int; the epoch at which broker requested
        "producerId": 17 # type : int; producer id requested 
    },
    "timestamp": str(timestamp_now+240) # type :  timestamp

})

#creating a partition record
send_request(5012, 'create_partition', method='POST', payload={
    "type": "metadata",
    "name": "PartitionRecord",
    "fields": {
        "partitionId": 4,
        "topicUUID": "123456",
        "replicas": [1, 2, 3],
        "ISR": [1, 2,3],
        "removingReplicas": [],
        "addingReplicas": [],
        "leader": "1",
        "partitionEpoch": 1
    },
    "timestamp": str(timestamp_now+240)
})

send_request(5012, 'client_mgmt', method='POST', payload = {"timestamp":str(timestamp_now)})
