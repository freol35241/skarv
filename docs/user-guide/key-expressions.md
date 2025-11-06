# Key Expressions

Key expressions are the foundation of Skarv's message routing system. They allow you to organize and route messages using hierarchical patterns and wildcards.

## Basic Syntax

Key expressions use a hierarchical structure with forward slashes (`/`) as separators:

```
level1/level2/level3
```

### Examples

```python
# Simple hierarchical keys
skarv.put("sensor/temperature", 22.5)
skarv.put("device/001/status", "online")
skarv.put("user/preferences/theme", "dark")
```

## Pattern Matching

Skarv supports several wildcard patterns for flexible message routing:

### Single Level Wildcard (`*`)

Matches exactly one level in the hierarchy:

```python
# Subscribe to any device status
@skarv.subscribe("device/*/status")
def handle_device_status(sample):
    device_id = str(sample.key_expr).split('/')[1]
    print(f"Device {device_id}: {sample.value}")

# This will match:
skarv.put("device/001/status", "online")  # ✅
skarv.put("device/002/status", "offline") # ✅
skarv.put("device/status", "error")       # ❌ (missing level)
skarv.put("device/001/status/extra", "x") # ❌ (too many levels)
```

### Multi-Level Wildcard (`**`)

Matches zero or more levels in the hierarchy:

```python
# Subscribe to all sensor data
@skarv.subscribe("sensor/**")
def handle_all_sensors(sample):
    print(f"All sensors - {sample.key_expr}: {sample.value}")

# This will match:
skarv.put("sensor/temperature", 22.5)           # ✅
skarv.put("sensor/room1/temperature", 23.1)     # ✅
skarv.put("sensor/building/a/floor/2/temp", 24) # ✅
skarv.put("sensor", "general")                  # ✅
```

### Mixed Patterns

You can combine exact matches with wildcards:

```python
# Subscribe to temperature readings from any room
@skarv.subscribe("sensor/*/temperature")

# Subscribe to any sensor in room1
@skarv.subscribe("sensor/room1/*")

# Subscribe to all data from device 001
@skarv.subscribe("device/001/**")
```

## Practical Examples

### IoT Device Management

```python
import skarv

# Device status monitoring
@skarv.subscribe("device/*/status")
def monitor_device_status(sample):
    device_id = str(sample.key_expr).split('/')[1]
    print(f"Device {device_id} status: {sample.value}")

# Temperature monitoring for all rooms
@skarv.subscribe("sensor/*/temperature")
def monitor_temperatures(sample):
    room = str(sample.key_expr).split('/')[1]
    print(f"Room {room} temperature: {sample.value}°C")

# All sensor data logging
@skarv.subscribe("sensor/**")
def log_all_sensors(sample):
    print(f"Sensor log: {sample.key_expr} = {sample.value}")

# Simulate device network
skarv.put("device/001/status", "online")
skarv.put("device/002/status", "offline")
skarv.put("sensor/living/temperature", 22.5)
skarv.put("sensor/bedroom/temperature", 21.8)
skarv.put("sensor/kitchen/humidity", 65.2)
```

### Application Event System

```python
import skarv

# User action events
@skarv.subscribe("user/*/action")
def handle_user_actions(sample):
    user_id = str(sample.key_expr).split('/')[1]
    print(f"User {user_id} performed action: {sample.value}")

# System events
@skarv.subscribe("system/**")
def handle_system_events(sample):
    print(f"System event: {sample.key_expr} - {sample.value}")

# Error logging
@skarv.subscribe("**/error")
def handle_errors(sample):
    print(f"Error in {sample.key_expr}: {sample.value}")

# Simulate application events
skarv.put("user/123/action", "login")
skarv.put("user/456/action", "logout")
skarv.put("system/startup", "Application started")
skarv.put("system/database/connection", "Connected")
skarv.put("user/123/error", "Invalid password")
```

## Retrieving Data with Patterns

The `skarv.get()` function supports both exact key lookups and pattern matching:

```python
# Store some data
skarv.put("device/001/temperature", 23.5)
skarv.put("device/002/temperature", 24.1)
skarv.put("device/001/humidity", 65.2)
skarv.put("device/002/humidity", 68.1)

# Retrieve a single value (non-wildcard key)
temp = skarv.get("device/001/temperature")
print(temp)
# Output: Sample(key_expr='device/001/temperature', value=23.5)

# Non-existent keys return None
missing = skarv.get("device/999/temperature")
print(missing)
# Output: None

# Retrieve all temperatures (wildcard key)
temperatures = skarv.get("device/*/temperature")
print(temperatures)
# Output: [Sample(key_expr='device/001/temperature', value=23.5),
#          Sample(key_expr='device/002/temperature', value=24.1)]

# Retrieve all data for device 001 (wildcard key)
device_001_data = skarv.get("device/001/*")
print(device_001_data)
# Output: [Sample(key_expr='device/001/temperature', value=23.5),
#          Sample(key_expr='device/001/humidity', value=65.2)]

# Retrieve all sensor data (wildcard key)
all_sensors = skarv.get("**")
print(all_sensors)
# Output: All stored samples as a list
```

**Note**: `skarv.get()` returns different types based on the key:

- **Non-wildcard keys** (e.g., `"device/001/temperature"`): Returns a single `Sample` or `None` if not found
- **Wildcard keys** (e.g., `"device/*/temperature"` or `"**"`): Returns a `list` of `Sample` objects (empty list if no matches)

## Best Practices

### 1. Use Hierarchical Structure

Organize your keys in a logical hierarchy:

```python
# Good
skarv.put("sensor/room1/temperature", 22.5)
skarv.put("sensor/room1/humidity", 65.2)
skarv.put("device/001/status", "online")

# Avoid flat structures
skarv.put("temperature_room1", 22.5)  # Less flexible
```

### 2. Be Specific with Subscriptions

Use specific patterns to avoid unintended matches:

```python
# Specific subscription
@skarv.subscribe("sensor/*/temperature")  # Only temperature sensors

# Too broad
@skarv.subscribe("**")  # Everything - use with caution
```

### 3. Plan Your Key Structure

Design your key hierarchy before implementation:

```
application/
├── user/
│   ├── {user_id}/
│   │   ├── profile
│   │   ├── preferences
│   │   └── actions
├── system/
│   ├── status
│   ├── events
│   └── errors
└── data/
    ├── sensor/
    │   └── {sensor_id}/
    └── device/
        └── {device_id}/
```

### 4. Use Consistent Naming

Maintain consistent naming conventions:

```python
# Use lowercase with underscores or hyphens
skarv.put("user_profile", {...})
skarv.put("system-status", "running")

# Avoid mixed case or special characters
skarv.put("UserProfile", {...})  # Inconsistent
skarv.put("system@status", "x")  # Special characters
```

## Advanced Patterns

### Conditional Subscriptions

You can use multiple subscriptions for complex routing:

```python
# Handle different types of alerts
@skarv.subscribe("alert/critical/**")
def handle_critical_alerts(sample):
    print(f"🚨 CRITICAL: {sample.value}")

@skarv.subscribe("alert/warning/**")
def handle_warning_alerts(sample):
    print(f"⚠️  WARNING: {sample.value}")

@skarv.subscribe("alert/info/**")
def handle_info_alerts(sample):
    print(f"ℹ️  INFO: {sample.value}")
```

### Data Aggregation

Use patterns to aggregate related data:

```python
# Aggregate all temperature readings
@skarv.subscribe("sensor/*/temperature")
def aggregate_temperatures(sample):
    # Get all current temperatures
    all_temps = skarv.get("sensor/*/temperature")
    avg_temp = sum(s.value for s in all_temps) / len(all_temps)
    print(f"Average temperature: {avg_temp}°C")
```

## Next Steps

- [Middleware](middleware.md) - Transform data with middleware
- [Examples](examples.md) - See more practical examples
- [API Reference](../api/core.md) - Complete API documentation 