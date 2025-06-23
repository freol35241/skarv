# Middleware

Middleware in Skarv allows you to transform, filter, and process data as it flows through the system. Middleware functions are applied to data before it reaches subscribers, enabling powerful data processing capabilities.

## How Middleware Works

Middleware functions are registered for specific key patterns and are executed in sequence when data is published:

```
skarv.put() → Middleware 1 → Middleware 2 → ... → Storage → Subscribers
```

If any middleware returns `None`, the data flow stops and the value is not stored or sent to subscribers.

## Built-in Middleware

Skarv provides several built-in middleware functions for common data processing tasks.

### Throttling

Limit the rate of data updates to prevent overwhelming subscribers:

```python
from skarv.middlewares import throttle
import skarv

# Allow temperature updates at most once every 5 seconds
skarv.register_middleware("sensor/temperature", throttle(5.0))

@skarv.subscribe("sensor/temperature")
def handle_temperature(sample):
    print(f"Temperature: {sample.value}°C")

# These will be throttled
skarv.put("sensor/temperature", 22.5)  # ✅ First update
skarv.put("sensor/temperature", 23.1)  # ❌ Throttled (too soon)
skarv.put("sensor/temperature", 22.8)  # ❌ Throttled (too soon)
```

### Averaging

Compute moving averages over a window of samples:

```python
from skarv.middlewares import average
import skarv

# Average humidity readings over 10 samples
skarv.register_middleware("sensor/humidity", average(10))

@skarv.subscribe("sensor/humidity")
def handle_humidity(sample):
    print(f"Average humidity: {sample.value}%")

# Add some readings
for i in range(15):
    skarv.put("sensor/humidity", 60 + i)
    # First 9 updates will show individual values
    # Updates 10+ will show moving averages
```

### Weighted Averaging

Compute weighted moving averages with more recent values having higher weight:

```python
from skarv.middlewares import weighted_average
import skarv

# Weighted average over 5 samples
skarv.register_middleware("sensor/pressure", weighted_average(5))

@skarv.subscribe("sensor/pressure")
def handle_pressure(sample):
    print(f"Weighted average pressure: {sample.value} hPa")
```

### Differentiation

Compute the numerical derivative of values over time:

```python
from skarv.middlewares import differentiate
import skarv

# Compute rate of change for temperature
skarv.register_middleware("sensor/temperature", differentiate())

@skarv.subscribe("sensor/temperature")
def handle_temperature_rate(sample):
    if sample.value is not None:
        print(f"Temperature rate: {sample.value}°C/s")
    else:
        print("First temperature reading - no rate available")

# Add readings with time intervals
skarv.put("sensor/temperature", 20.0)
time.sleep(1)
skarv.put("sensor/temperature", 22.0)  # Rate: 2.0°C/s
time.sleep(1)
skarv.put("sensor/temperature", 21.5)  # Rate: -0.5°C/s
```

### Batching

Collect multiple values and emit them as a batch:

```python
from skarv.middlewares import batch
import skarv

# Collect 5 sensor readings before emitting
skarv.register_middleware("sensor/readings", batch(5))

@skarv.subscribe("sensor/readings")
def handle_batch(sample):
    print(f"Batch of {len(sample.value)} readings: {sample.value}")

# Add individual readings
for i in range(7):
    skarv.put("sensor/readings", f"reading_{i}")
    # First 4 updates: no output (collecting)
    # 5th update: batch of 5 readings
    # 6th update: no output (collecting for next batch)
    # 7th update: batch of 2 readings (if we stop here)
```

## Combining Middleware

You can register multiple middleware functions for the same key pattern. They will be executed in the order of registration:

```python
from skarv.middlewares import throttle, average
import skarv

# First throttle, then average
skarv.register_middleware("sensor/temperature", throttle(2.0))
skarv.register_middleware("sensor/temperature", average(5))

@skarv.subscribe("sensor/temperature")
def handle_processed_temperature(sample):
    print(f"Processed temperature: {sample.value}°C")

# This will:
# 1. Throttle to at most once every 2 seconds
# 2. Average over 5 samples
# 3. Send to subscribers
```

## Custom Middleware

You can create your own middleware functions. A middleware function should:

1. Take a value as input
2. Return the processed value or `None` to stop the flow

### Example: Data Validation

```python
def validate_temperature(value):
    """Validate temperature readings are within reasonable range."""
    if isinstance(value, (int, float)) and -50 <= value <= 100:
        return value
    else:
        print(f"Invalid temperature: {value}")
        return None

# Register custom middleware
skarv.register_middleware("sensor/temperature", validate_temperature)

@skarv.subscribe("sensor/temperature")
def handle_valid_temperature(sample):
    print(f"Valid temperature: {sample.value}°C")

# Test with valid and invalid data
skarv.put("sensor/temperature", 22.5)  # ✅ Valid
skarv.put("sensor/temperature", 150)   # ❌ Invalid (too high)
skarv.put("sensor/temperature", "hot") # ❌ Invalid (not numeric)
```

### Example: Data Transformation

```python
def celsius_to_fahrenheit(value):
    """Convert Celsius to Fahrenheit."""
    if isinstance(value, (int, float)):
        return (value * 9/5) + 32
    return None

def add_timestamp(value):
    """Add timestamp to data."""
    import time
    return {
        "value": value,
        "timestamp": time.time()
    }

# Register transformation middleware
skarv.register_middleware("sensor/temperature", celsius_to_fahrenheit)
skarv.register_middleware("sensor/temperature", add_timestamp)

@skarv.subscribe("sensor/temperature")
def handle_transformed_temperature(sample):
    print(f"Temperature: {sample.value['value']}°F at {sample.value['timestamp']}")

skarv.put("sensor/temperature", 22.5)
# Output: Temperature: 72.5°F at 1640995200.123
```

### Example: Data Filtering

```python
def filter_outliers(value, threshold=10):
    """Filter out values that differ too much from the previous value."""
    def filter_func(current_value):
        if not hasattr(filter_func, 'last_value'):
            filter_func.last_value = current_value
            return current_value
        
        if abs(current_value - filter_func.last_value) > threshold:
            print(f"Outlier detected: {current_value} (diff: {abs(current_value - filter_func.last_value)})")
            return None
        
        filter_func.last_value = current_value
        return current_value
    
    return filter_func

# Register outlier filter
skarv.register_middleware("sensor/temperature", filter_outliers(threshold=5))

@skarv.subscribe("sensor/temperature")
def handle_filtered_temperature(sample):
    print(f"Filtered temperature: {sample.value}°C")

# Test with normal and outlier data
skarv.put("sensor/temperature", 22.0)  # ✅ First reading
skarv.put("sensor/temperature", 24.0)  # ✅ Normal change
skarv.put("sensor/temperature", 35.0)  # ❌ Outlier (diff > 5)
skarv.put("sensor/temperature", 25.0)  # ✅ Normal change
```

## Middleware Best Practices

### 1. Order Matters

Register middleware in the order you want them executed:

```python
# Good: Filter first, then process
skarv.register_middleware("sensor/*", validate_data)
skarv.register_middleware("sensor/*", average(10))

# Avoid: Processing before filtering
skarv.register_middleware("sensor/*", average(10))
skarv.register_middleware("sensor/*", validate_data)  # Too late!
```

### 2. Handle None Returns

Always check if middleware returns `None`:

```python
def safe_middleware(value):
    if value is None:
        return None  # Stop the flow
    # Process the value
    return processed_value
```

### 3. Use Specific Key Patterns

Register middleware for specific keys to avoid unintended processing:

```python
# Specific to temperature sensors
skarv.register_middleware("sensor/*/temperature", throttle(5.0))

# Avoid overly broad patterns
skarv.register_middleware("**", some_middleware)  # Processes everything!
```

### 4. Consider Performance

Middleware runs synchronously, so keep it fast:

```python
# Good: Fast operation
def fast_middleware(value):
    return value * 2

# Avoid: Slow operations in middleware
def slow_middleware(value):
    time.sleep(1)  # Blocks the entire flow!
    return value
```

## Real-World Example: Sensor Data Pipeline

```python
import skarv
from skarv.middlewares import throttle, average, differentiate
import time

# Set up a complete sensor data pipeline
def setup_sensor_pipeline():
    # Temperature pipeline
    skarv.register_middleware("sensor/temperature", throttle(1.0))  # Max 1 update/sec
    skarv.register_middleware("sensor/temperature", average(5))     # 5-sample average
    skarv.register_middleware("sensor/temperature", differentiate()) # Rate of change
    
    # Humidity pipeline
    skarv.register_middleware("sensor/humidity", throttle(2.0))     # Max 1 update/2sec
    skarv.register_middleware("sensor/humidity", average(3))        # 3-sample average
    
    # Pressure pipeline
    skarv.register_middleware("sensor/pressure", batch(10))         # Batch 10 readings

# Subscribers for processed data
@skarv.subscribe("sensor/temperature")
def handle_processed_temperature(sample):
    if sample.value is not None:
        print(f"🌡️  Processed temp: {sample.value}°C/s (rate of change)")

@skarv.subscribe("sensor/humidity")
def handle_processed_humidity(sample):
    print(f"💧 Processed humidity: {sample.value}% (averaged)")

@skarv.subscribe("sensor/pressure")
def handle_batched_pressure(sample):
    print(f"📊 Pressure batch: {len(sample.value)} readings")

# Set up the pipeline
setup_sensor_pipeline()

# Simulate sensor data
def simulate_sensors():
    for i in range(20):
        skarv.put("sensor/temperature", 20 + i * 0.5)
        skarv.put("sensor/humidity", 60 + i * 2)
        skarv.put("sensor/pressure", 1000 + i * 5)
        time.sleep(0.5)

# Run the simulation
simulate_sensors()
```

## Next Steps

- [Examples](examples.md) - See more practical examples
- [API Reference](../api/middleware.md) - Complete middleware API documentation
- [Core API](../api/core.md) - Learn about core Skarv functions 