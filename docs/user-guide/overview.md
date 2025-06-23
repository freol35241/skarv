# Overview

## Architecture

Skarv is designed as a simple, in-memory message broker with the following architecture:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Publishers    │    │   Middleware    │    │   Subscribers   │
│                 │    │                 │    │                 │
│ skarv.put()     │───▶│ Transform Data  │───▶│ @skarv.subscribe│
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   In-Memory     │
                       │     Vault       │
                       │                 │
                       │ skarv.get()     │
                       └─────────────────┘
```

## Core Components

### 1. Vault (Storage)

The vault is an in-memory dictionary that stores all published data. It's thread-safe and uses locks to ensure data consistency.

```python
# Data is stored as key-value pairs
_vault = {
    "sensor/temperature": 22.5,
    "device/001/status": "online",
    "user/preferences": {"theme": "dark"}
}
```

### 2. Subscribers

Subscribers are functions that listen for data matching specific key patterns. They are automatically called when matching data is published.

```python
@skarv.subscribe("sensor/*")
def handle_sensor_data(sample):
    # This function is called whenever data matching "sensor/*" is published
    process_sensor_data(sample.value)
```

### 3. Middleware

Middleware functions transform data as it flows through the system. They can filter, modify, or aggregate data before it reaches subscribers.

```python
# Throttle updates to prevent spam
skarv.register_middleware("sensor/temperature", throttle(5.0))

# Average readings over time
skarv.register_middleware("sensor/humidity", average(10))
```

### 4. Key Expressions

Key expressions provide flexible message routing using patterns and wildcards:

- `sensor/temperature` - Exact match
- `sensor/*` - Any sensor reading
- `device/*/status` - Status of any device
- `**` - Everything

## Data Flow

Here's how data flows through Skarv:

1. **Publish**: `skarv.put("sensor/temperature", 22.5)`
2. **Middleware Processing**: Data passes through registered middleware
3. **Storage**: Data is stored in the vault
4. **Subscription Notification**: Matching subscribers are notified
5. **Retrieval**: Data can be retrieved with `skarv.get()`

## Thread Safety

All Skarv operations are thread-safe:

- **Vault Access**: Protected by locks
- **Subscriber Management**: Thread-safe set operations
- **Middleware Processing**: Each middleware has its own lock

This means you can safely use Skarv in multi-threaded applications.

## Performance Characteristics

### Strengths

- **Low Latency**: In-memory operations are very fast
- **Simple**: Minimal overhead from complex routing
- **Predictable**: Synchronous operations are easy to debug

### Limitations

- **Memory Bound**: All data must fit in memory
- **Single Process**: No distributed capabilities
- **No Persistence**: Data is lost on restart

## Use Cases

### Ideal For

- **Real-time Dashboards**: Display live sensor data
- **Event Processing**: Handle application events
- **Data Pipelines**: Simple ETL processes
- **Prototyping**: Quick message broker setup
- **IoT Applications**: Connect sensors to processing logic

### Example: Sensor Network

```python
import skarv
import time

# Set up middleware for data processing
skarv.register_middleware("sensor/temperature", average(5))
skarv.register_middleware("sensor/humidity", throttle(2.0))

# Dashboard subscribers
@skarv.subscribe("sensor/temperature")
def update_temperature_display(sample):
    print(f"🌡️  {sample.value}°C")

@skarv.subscribe("sensor/humidity")
def update_humidity_display(sample):
    print(f"💧 {sample.value}%")

@skarv.subscribe("alert/*")
def handle_alerts(sample):
    print(f"🚨 {sample.value}")

# Simulate sensor network
def sensor_network():
    while True:
        # Simulate sensor readings
        temp = 20 + random.uniform(-5, 5)
        humidity = 60 + random.uniform(-10, 10)
        
        skarv.put("sensor/temperature", round(temp, 1))
        skarv.put("sensor/humidity", round(humidity, 1))
        
        # Generate alerts
        if temp > 25:
            skarv.put("alert/temperature", "High temperature detected!")
        
        time.sleep(1)

# Start the network
sensor_network()
```

## Next Steps

- [Key Expressions](key-expressions.md) - Learn about pattern matching
- [Middleware](middleware.md) - Transform and filter data
- [Examples](examples.md) - See more practical examples 