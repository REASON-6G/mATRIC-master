# mATRIC backend

## Agent:

It comprises two parts: 
1.	base_agent. py includes functions to authenticate with mATRIC backend and get onboard, refresh authentication token if required, send geolocation data and send periodic updates with a settings file 
2.	second part for specific agents/access points ie.Nokia to extend/override the methods in base_agent and develop code for extracting access point data and receive/execute commands sent by third party apps 

Upon registration of a new agent by an Admin user, the agent gets assigned a unique agent Id and a password ang get shipped to be installed on the specific access point, developers should extend the base code to retrieve data from access point and send it to mATRIC.

When the agent is run for the first time it calls relevant mATRIC backend API endpoint with the agent Id and password registered in the settings file to authenticate and onboard itself, then it will send its configurations including the base API URL  to receive command, list of executable commands on access point and geolocation data to the backend used for mapping out connected access points.

The authenticated and onboard agent can send regular updates to mATRIC backend API, the payload will be saved in InfluxDB.

## FastAPI Backend

The backend facilitates authentication for users, agents and third-party-apps, receives regular updates from connected agents, provides third party app with connection to agent configuration and data, sends commands/instruction from third party apps to the agents. To ensure resilience, reliability and scalability, messaging queue RabbitMQ is incorporated into the architecture where FastAPI publishes requests received from endpoints through RabbitMQ, its publisher redirects the requests to relevant subscribers for processing and action.

FastAPI backend comprises several nodes carrying different tasks, below is a non-exhaustive list of them:

**User operations:** An Admin user will be able to add/create new user per request, using the endpoint:
- Post /users: add/create new user
- Put users/username: update a user
- Delete users/username: delete a user
- Get /users/me: return current user
- Get /users: return list of all users

**Agents operations:** An Admin user will be able to register a new agent using endpoints below:
- Post /agents: add/create a new agent
- Get /agents/agent Id: get the agent by agent Id
- Put /agents/agent Id: update agent details
- Delete /agents/agent Id: remove the agent from database

**Third party app operations:** An Admin user will be able to register a new third party app and generate API key for them, endpoints below are dedicated to handling the operation of third party apps:

- Post /third_party_apps: add/crate a new third party app
- Get /third_party_apps/app Id: get third party app by id
- Put  /third_party_apps/app Id: update third party app details
- Delete  /third_party_apps/app Id: remove third party app details from database

## Agents sending updates:

An authenticated and onboard agent can send regular updates to the backend by calling the /agent_update/update endpoint. Developers extend/override the base_agent class to retrieve data from the access point. By calling the endpoint with a JSON payload of data, FastAPI will run the RabbitMQ publisher and its subscriber will receive and save the payload into InfluxDB. The process is data agnostic and will work through the JSON object key/values to write them into database. Considering InfluxDB will save the data with type associated with them, developers should make sure any data they send is of the correct type (integer, float, string etc) and the payload is a valid JSON.

## Third party apps get agents details:

A registered and authenticated app can interact with the backend/agents to retrieve data. The app can call the endpoint /agent_details/request_all_agents_details and retrieve a list of all active agents with their Ids and their configurations including any command/instruction they may receive/execute. Agent Id will be used to retrieve agent specific data and configuration list will be used to send commands/instructions to the agent.
After sending the request to fetch list of agents and their details, FastAPI will publish the request using RabbitMQ and a subscriber will pick up the request, process it and send the results back to a FastAPI call back endpoint so they get published through a WebSocket back to the original requester.

## Third party app get agents data:

using the retrieved agent Id, the app calls endpoint /agent_data/request_agent_data and subscribes to receive agent(s) specific data. The app will process the data and considering its internal logic, it might send specific commands back to the agent, for instance if no one subscribed to the access point, the app might send a command to agent turn itself off.
The technical flow in this scenario is similar to what happens to request to get list of agents above.

## Third party apps sending commands back to agents:

the app can subscribe to get agent data from InfluxDB and process the data. Based on the process it might send a command/instruction back to the agent/access point calling send_command/send_command. As multiple apps might connect to the backend services and sending competing commands, a Conflict Resolution Layer (CRL) is developed to mitigate/resolve race conditions: in the scenario one app sends a “turn off” command to the agent and a second app sends a “turn on” command, the resolution layer will apply its logic and select which competing command can go through, the command will be passed through RabbitMQ similar to the scenarios discussed earlier and the subscriber will pass the command in an API call to the agent/access point. Developers decide which API to install on the access point and how they process the call from subscriber.

**A sample of config payload from agent:**
```
Config = {“geolocation”: {“lat”: “value”, “long”: “value”},
	      “api_url”: “base_api_url”,
	     “commands”: [“command0”, “command1”, …]
	     }
```
Note that mATRIC will send the command sent by third_party_app to the URL /base_api_url/agent_id.
The config payload should include at least three key/value pair in the sample.

## PostgreSQL:

PostgreSQL is used to manage the details for users, agents and third-party-apps. Currently it includes three tables: users, agents and third_party_apps. Database models can get deployed using Alembic. Database settings are defined in the config file, sample below:
```
db_username: str
db_password: str 
db_host: str
db_port: int
db_name: str
```

## InfluxDB:

Project uses InfluxDB to save time series data received from agents, InlfuxDB settings are defined in the config file.

## RabbitMQ:

Project uses RabbitMQ as the messaging queue for reliability and scalability. When an authenticated user/agent/third-party-app calls an API endpoint with a specific request, FastAPI runs a RabbitMQ publisher to publish the request to a channel, a subscriber will receive the message and process the request. Subscriber might send a message to a call back endpoint if required.
