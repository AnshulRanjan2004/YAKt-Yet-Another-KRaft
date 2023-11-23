# YAKt (Yet Another KRaft)

YAKt is a project that involves the implementation of the KRaft protocol from scratch, focusing on managing metadata for the Kafka system. The project encompasses a deep dive into concepts such as the Raft Consensus algorithm, Leader Election, Log Replication, Fault Tolerance, ZAB Consensus algorithm, Kraft and Zookeeper Architecture, Event-driven Architecture, and Kafka Architecture.

## Project Objectives and Outcomes

### Objectives

- Gain a deeper understanding of Raft Consensus and related algorithms.
- Explore the nuances of Kraft, Zookeeper Architecture, and Kafka Architecture.
- Implement an event-driven architecture for managing metadata.
- Develop a robust system mimicking the working of KRaft.

### Outcomes

- A functioning system with real-world use cases.
- Enhanced knowledge of consensus algorithms and distributed systems.

## Raft Node

The Raft Node component of YAKt is designed to handle key functionalities:

- **Leader Election**: Selecting the leader for the KRaft cluster.
- **Event-driven Architecture**: Implementing an event-driven model for efficient communication.
- **Failover Management**: Providing standard Raft failover guarantees.
- **Maintaining Event Log**: Keeping a log of all changes made for reconstructing the metadata store.
- **Snapshotting**: Creating and retrieving snapshots of the event log for fault tolerance.

## Records and Limitations/Modifications

The YAKt project introduces several record types with specific structures:

1. **Register Broker Records**
2. **Topic Records**
3. **Partition Records**
4. **ProducerIDsRecord**
5. **BrokerRegistrationChangeBrokerRecord**

These records follow the outlined structures and are essential for managing metadata in the KRaft cluster.

## Broker Management API

YAKt provides a comprehensive Broker Management API with endpoints for registering brokers, fetching active brokers, getting brokers by ID, and more.

### Endpoints

1. **RegisterBrokerRecord**
   - `register`: Register a new broker.
   - `get_all_active_brokers`: Get information about all active brokers.
   - `get_broker_by_id`: Retrieve details of a specific broker by ID.

2. **TopicRecord**
   - `create_topic`: Create a new topic.
   - `get_topic_by_name`: Retrieve details of a topic by name.

3. **PartitionRecord**
   - `create_partition`: Create a new partition.
   - `remove_replica`: Remove a replica from a partition.
   - `add_replica`: Add a replica to a partition.

4. **ProducerIdsRecord**
   - `register_producer`: Register a new producer.

5. **BrokerRegistrationChangeBrokerRecord**
   - `register_broker_change`: Register changes to a broker.
   - `unregister_broker`: Unregister a broker

6. **BrokerMgmt**
   - `broker_mgmt`: Retrieve metadata updates since a specified timestamp.

7. **ClientMgmt**
   - `client_mgmt`: Retrieve metadata updates for clients since a specified timestamp.

## Getting Started

### Prerequisites

- Python
- Flask
- PyRaft
- Telnetlib

### Installation

1. Clone the repository:

   ```bash
   git clone git@github.com:Cloud-Computing-Big-Data/RR-Team-8-YAKt-Yet-Another-KRaft-.git
   cd RR-Team-8-YAKt-Yet-Another-KRaft-
   ```
2. Install Dependencies

   ```bash
   pip install -r requirements.txt
   ```
3. Run the application

   ```bash
   python3 new_run.py -a 127.0.0.1:5010 -i 1
   ```

 - Note: This Project Uses `pyraft` as it's underlying implementation of the Raft Consensus Algorithm <br>
`Refer how to run a Raft Cluster using pyraft here:` - [PyRaft](https://pypi.org/project/pyraft/) <br>
 Replace `run_raft.py` with `new_run.py` which is included in this project
