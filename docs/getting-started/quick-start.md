# Quick Start

This guide will walk you through the basic concepts and operations in Skarv.

## Basic Concepts

Skarv is built around three main concepts:

1. **Publishing**: Putting data into the system with a key
2. **Subscribing**: Listening for data with matching keys
3. **Retrieving**: Getting stored data by key patterns

## Your First Skarv Application

Let's create a simple sensor monitoring system:

```python
import skarv
import time

# Subscribe to temperature sensor data
@skarv.subscribe("sensor/temperature")
def handle_temperature(sample):
    print(f"Temperature: {sample.value}°C")

# Subscribe to all sensor data
@skarv.subscribe("sensor/*")
def handle_all_sensors(sample):
    print(f"All sensors - {sample.key_expr}: {sample.value}")

# Simulate sensor readings
skarv.put("sensor/temperature", 22.5)
skarv.put("sensor/humidity", 65.2)
skarv.put("sensor/pressure", 1013.25)

# Wait a moment for processing
time.sleep(0.1)
```

This will output:
```
Temperature: 22.5°C
All sensors - sensor/temperature: 22.5
All sensors - sensor/humidity: 65.2
All sensors - sensor/pressure: 1013.25
```

## Key Expressions

Skarv uses key expressions for flexible message routing:

```python
# Exact match
skarv.put("device/001/status", "online")

# Wildcard patterns
@skarv.subscribe("device/*/status")  # Matches any device status
@skarv.subscribe("sensor/**")        # Matches all sensor data
@skarv.subscribe("*/temperature")    # Matches any temperature reading
```

## Retrieving Data

You can retrieve stored data using key patterns:

```python
# Store some data
skarv.put("device/001/temperature", 23.5)
skarv.put("device/002/temperature", 24.1)
skarv.put("device/001/humidity", 65.2)

# Retrieve all device temperatures
temperatures = skarv.get("device/*/temperature")
print(temperatures)
# Output: [Sample(key_expr='device/001/temperature', value=23.5), 
#          Sample(key_expr='device/002/temperature', value=24.1)]

# Retrieve all data for device 001
device_001_data = skarv.get("device/001/*")
print(device_001_data)
# Output: [Sample(key_expr='device/001/temperature', value=23.5),
#          Sample(key_expr='device/001/humidity', value=65.2)]
```

## Using Middleware

Middleware allows you to transform data as it flows through the system:

```python
import skarv
from skarv.middlewares import throttle, average

# Throttle temperature updates to at most once every 5 seconds
skarv.register_middleware("sensor/temperature", throttle(5.0))

# Average humidity readings over 10 samples
skarv.register_middleware("sensor/humidity", average(10))

@skarv.subscribe("sensor/temperature")
def handle_throttled_temperature(sample):
    print(f"Throttled temperature: {sample.value}°C")

@skarv.subscribe("sensor/humidity")
def handle_averaged_humidity(sample):
    print(f"Averaged humidity: {sample.value}%")

# These will be processed by middleware
skarv.put("sensor/temperature", 22.5)
skarv.put("sensor/humidity", 65.2)
```

## Complete Example: IoT Dashboard

Here's a more complete example simulating an IoT dashboard:

```python
import skarv
import time
import random

# Dashboard handlers
@skarv.subscribe("sensor/temperature")
def update_temperature_display(sample):
    print(f"🌡️  Temperature: {sample.value}°C")

@skarv.subscribe("sensor/humidity")
def update_humidity_display(sample):
    print(f"💧 Humidity: {sample.value}%")

@skarv.subscribe("device/*/status")
def update_device_status(sample):
    device_id = str(sample.key_expr).split('/')[1]
    print(f"📱 Device {device_id}: {sample.value}")

@skarv.subscribe("alert/*")
def handle_alerts(sample):
    print(f"🚨 ALERT: {sample.key_expr} - {sample.value}")

# Simulate sensor readings
def simulate_sensors():
    while True:
        # Temperature fluctuates around 22°C
        temp = 22 + random.uniform(-2, 2)
        skarv.put("sensor/temperature", round(temp, 1))
        
        # Humidity fluctuates around 65%
        humidity = 65 + random.uniform(-5, 5)
        skarv.put("sensor/humidity", round(humidity, 1))
        
        # Check for alerts
        if temp > 24:
            skarv.put("alert/high_temperature", f"Temperature too high: {temp}°C")
        
        time.sleep(2)

# Start simulation
print("Starting IoT Dashboard...")
simulate_sensors()
```

## Next Steps

Now that you understand the basics:

- [Learn about Key Expressions](../user-guide/key-expressions.md)
- [Explore Middleware](../user-guide/middleware.md)
- [See More Examples](../user-guide/examples.md)
- [Check the API Reference](../api/core.md) 