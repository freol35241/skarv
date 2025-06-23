# Welcome to Skarv

> **skarv** is a Swedish noun that refers to the point where two things are joined together. Translations to English include joint, splice, connection and similar words. Interestingly, it is also the Swedish word for cormorant (the bird).

## What is Skarv?

Skarv is a simple, synchronous, thread-safe, single process, in-memory message broker written in Python. It provides a minimalist API for processing real-time data from multiple sources to multiple sinks with intermediate processing capabilities.

## Why Skarv?

Skarv was created to provide the most simplistic API possible for real-time data processing. When you need to:

- **Connect multiple data sources** to multiple consumers
- **Process data in real-time** with minimal latency
- **Apply transformations** to data streams
- **Keep things simple** without the complexity of distributed systems

Skarv offers a lightweight, in-memory solution that's perfect for single-process applications that need message routing and processing capabilities.

## How does Skarv work?

Skarv leverages the concept of **Key Expressions** from [Zenoh](https://zenoh.io/) to provide flexible message routing. Here's how it works:

### Core Concepts

1. **Key Expressions**: Messages are identified by key expressions (e.g., `sensor/temperature`, `device/*/status`)
2. **In-Memory Storage**: All data is stored in memory for maximum performance
3. **Thread-Safe Operations**: All operations are thread-safe using locks
4. **Middleware Support**: Transform data as it flows through the system

### Basic Operations

```python
import skarv

# Subscribe to messages
@skarv.subscribe("sensor/*")
def handle_sensor_data(sample):
    print(f"Received: {sample.key_expr} = {sample.value}")

# Publish a message
skarv.put("sensor/temperature", 23.5)

# Retrieve messages
samples = skarv.get("sensor/*")
```

### Key Features

- **Simple API**: Minimal learning curve
- **Thread-Safe**: Safe for concurrent access
- **Middleware Support**: Transform data on-the-fly
- **Pattern Matching**: Use wildcards and patterns for flexible routing
- **Synchronous**: Predictable, easy-to-debug behavior

## Quick Start

```bash
pip install skarv
```

```python
import skarv

# Subscribe to all sensor data
@skarv.subscribe("sensor/**")
def log_sensor_data(sample):
    print(f"Sensor {sample.key_expr}: {sample.value}")

# Add some data
skarv.put("sensor/temperature", 22.5)
skarv.put("sensor/humidity", 65.2)
skarv.put("sensor/pressure", 1013.25)
```

## When to Use Skarv

Skarv is ideal for:

- **IoT Applications**: Connecting sensors to processing logic
- **Data Pipelines**: Simple ETL processes
- **Event Systems**: Internal event routing
- **Prototyping**: Quick message broker setup
- **Single-Process Applications**: When distributed systems are overkill

## When Not to Use Skarv

Skarv is not suitable for:

- **Distributed Systems**: No network communication
- **Persistence**: Data is lost on restart
- **High Availability**: Single point of failure
- **Large Scale**: Limited by memory and single process

## Next Steps

- [Installation Guide](getting-started/installation.md)
- [Quick Start Tutorial](getting-started/quick-start.md)
- [API Reference](api/core.md)
- [Examples](user-guide/examples.md) 