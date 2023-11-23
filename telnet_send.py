import telnetlib
import json
import base64

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

def get_value(tn, key):
    # Get the value with the RESP command
    get_command = f'get {key}\r\n'
    response = send_command(tn, get_command)

    # Extract the length value
    length = int(response[1:])

    # Read the actual value
    value = tn.read_very_eager()

    # Decode the base64 value
    decoded_value = base64.b64decode(value).decode()
    print(decoded_value)

# Connect to the Telnet server
tn = telnetlib.Telnet("localhost", 5010)

# Example: Set RegisterBrokerRecord
register_broker_record = {
    "type": "metadata",
    "name": "RegisterBrokerRecord",
    "fields": {
        "internalUUID": "123",
        "brokerId": 0,
        "brokerHost": "",
        "brokerPort": "",
        "securityProtocol": "",
        "brokerStatus": "",
        "rackId": "",
        "epoch": 0
    }
}
set_value(tn, "RegisterBrokerRecord:internalUUID123", register_broker_record)

# Example: Get RegisterBrokerRecord
get_value(tn, "RegisterBrokerRecord:internalUUID123")

# Close the Telnet connection
tn.close()

