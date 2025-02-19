# UART Device Control

![System Architecture](window.png)

HTTP server that allows to read data and control and embedded device connected via UART interface.

## Getting Started  

### Install dependencies  
Ensure you have **Python 3.8+** installed. Then, install the required libraries:  
```bash
pip install -r requirements.txt
```

### Run the application  
Execute the `main.py` file:  
```bash
python main.py --simulate --gui
```

### Console parameters
| Parameter         | Type     | Default Value  | Description |
|------------------|---------|---------------|-------------|
| `--serial_port`  | `str`   | `/dev/ttyUSB0` | UART serial port |
| `--server_port`  | `int`   | `7100`        | API server port |
| `--host`         | `str`   | `localhost`   | API host address |
| `--baud_rate`    | `int`   | `115200`      | UART baudrate |
| `--simulation`   | `bool`  | `False`       | Enable simulation mode |
| `--gui`          | `bool`  | `False`       | Open a graphic interface |


## Configuration & API Usage  

### API Endpoints  

| Method | Endpoint         | Description |
|--------|-----------------|-------------|
| `GET`  | `/start`        | Starts the stream of messages |
| `GET`  | `/stop`         | Stops the stream of messages |
| `GET`  | `/messages?limit=[limit]` | Returns `limit` last received messages
| `PUT`  | `/configure`    | Configures frequency & debug mode |
| `GET`  | `/device`       | Fetches latest sensor data |

### Example API Requests  

Start the stream 
```bash
curl -X GET http://localhost:7100/start
```

Stop the stream 
```bash
curl -X GET http://localhost:7100/stop
```

Get the last 10 received messages
```bash
curl -X GET http://localhost:7100/messages?limit=10
```

Configure the device  
```bash
curl -X PUT http://localhost:7100/configure \
     -H "Content-Type: application/json" \
     -d '{"frequency": 10, "debug": true}'
```

Get sensor data  
```bash
curl -X GET http://localhost:7100/device
```
