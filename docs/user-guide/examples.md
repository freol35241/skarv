# Examples

This page contains practical examples demonstrating how to use Skarv in real-world scenarios.

## Basic Examples

### Simple Message Broker

```python
import skarv

# Set up subscribers
@skarv.subscribe("chat/messages")
def handle_chat_message(sample):
    print(f"💬 {sample.value}")

@skarv.subscribe("system/status")
def handle_system_status(sample):
    print(f"🖥️  System: {sample.value}")

# Send messages
skarv.put("chat/messages", "Hello, world!")
skarv.put("system/status", "Online")
skarv.put("chat/messages", "How are you?")

# Retrieve all messages
messages = skarv.get("chat/messages")
print(f"All messages: {messages}")
```

### Event Logging System

```python
import skarv
import time

# Log different types of events
@skarv.subscribe("log/info")
def log_info(sample):
    print(f"ℹ️  INFO: {sample.value}")

@skarv.subscribe("log/warning")
def log_warning(sample):
    print(f"⚠️  WARNING: {sample.value}")

@skarv.subscribe("log/error")
def log_error(sample):
    print(f"❌ ERROR: {sample.value}")

# Simulate application events
def simulate_application():
    skarv.put("log/info", "Application started")
    time.sleep(1)
    skarv.put("log/info", "Database connected")
    time.sleep(1)
    skarv.put("log/warning", "High memory usage detected")
    time.sleep(1)
    skarv.put("log/error", "Failed to connect to external service")

simulate_application()
```

## IoT and Sensor Examples

### Smart Home Monitoring

```python
import skarv
import time
import random

# Room monitoring
@skarv.subscribe("home/living/temperature")
def living_room_temp(sample):
    print(f"🏠 Living Room: {sample.value}°C")

@skarv.subscribe("home/bedroom/temperature")
def bedroom_temp(sample):
    print(f"🛏️  Bedroom: {sample.value}°C")

@skarv.subscribe("home/*/humidity")
def any_room_humidity(sample):
    room = str(sample.key_expr).split('/')[1]
    print(f"💧 {room.title()}: {sample.value}% humidity")

@skarv.subscribe("home/**")
def all_home_data(sample):
    print(f"📊 Home data: {sample.key_expr} = {sample.value}")

# Simulate smart home sensors
def simulate_smart_home():
    while True:
        # Living room sensors
        skarv.put("home/living/temperature", 22 + random.uniform(-1, 1))
        skarv.put("home/living/humidity", 45 + random.uniform(-5, 5))
        
        # Bedroom sensors
        skarv.put("home/bedroom/temperature", 20 + random.uniform(-1, 1))
        skarv.put("home/bedroom/humidity", 50 + random.uniform(-5, 5))
        
        time.sleep(2)

# Start simulation
print("🏠 Smart Home Monitoring Started")
simulate_smart_home()
```

### Industrial Sensor Network

```python
import skarv
from skarv.middlewares import throttle, average, differentiate
import time
import random

# Set up data processing pipeline
def setup_industrial_pipeline():
    # Temperature monitoring with processing
    skarv.register_middleware("factory/zone1/temperature", throttle(5.0))
    skarv.register_middleware("factory/zone1/temperature", average(10))
    skarv.register_middleware("factory/zone1/temperature", differentiate())
    
    # Pressure monitoring
    skarv.register_middleware("factory/zone1/pressure", average(5))
    
    # Vibration monitoring with batching
    skarv.register_middleware("factory/zone1/vibration", batch(20))

# Monitoring handlers
@skarv.subscribe("factory/zone1/temperature")
def monitor_temperature(sample):
    if sample.value is not None:
        print(f"🌡️  Zone 1 Temp Rate: {sample.value:.2f}°C/min")

@skarv.subscribe("factory/zone1/pressure")
def monitor_pressure(sample):
    print(f"📊 Zone 1 Pressure: {sample.value:.1f} bar")

@skarv.subscribe("factory/zone1/vibration")
def monitor_vibration(sample):
    print(f"📈 Zone 1 Vibration Batch: {len(sample.value)} readings")

@skarv.subscribe("factory/zone1/alarm")
def handle_alarm(sample):
    print(f"🚨 ALARM: {sample.value}")

# Simulate industrial sensors
def simulate_industrial_sensors():
    setup_industrial_pipeline()
    
    temp = 25.0
    pressure = 10.0
    
    while True:
        # Temperature with trend
        temp += random.uniform(-0.5, 0.5)
        skarv.put("factory/zone1/temperature", round(temp, 1))
        
        # Pressure fluctuations
        pressure += random.uniform(-0.2, 0.2)
        skarv.put("factory/zone1/pressure", round(pressure, 1))
        
        # Vibration readings
        for i in range(25):
            vibration = random.uniform(0, 10)
            skarv.put("factory/zone1/vibration", round(vibration, 2))
        
        # Check for alarms
        if temp > 30:
            skarv.put("factory/zone1/alarm", f"High temperature: {temp}°C")
        
        time.sleep(1)

print("🏭 Industrial Monitoring Started")
simulate_industrial_sensors()
```

## Application Examples

### Web Application Event System

```python
import skarv
import time
import random

# User session management
@skarv.subscribe("user/*/login")
def user_login(sample):
    user_id = str(sample.key_expr).split('/')[1]
    print(f"👤 User {user_id} logged in")

@skarv.subscribe("user/*/logout")
def user_logout(sample):
    user_id = str(sample.key_expr).split('/')[1]
    print(f"👋 User {user_id} logged out")

@skarv.subscribe("user/*/action")
def user_action(sample):
    user_id = str(sample.key_expr).split('/')[1]
    print(f"🎯 User {user_id} action: {sample.value}")

# System monitoring
@skarv.subscribe("system/performance/*")
def system_performance(sample):
    metric = str(sample.key_expr).split('/')[-1]
    print(f"⚡ {metric}: {sample.value}")

@skarv.subscribe("system/error/*")
def system_error(sample):
    error_type = str(sample.key_expr).split('/')[-1]
    print(f"❌ {error_type} error: {sample.value}")

# Simulate web application
def simulate_web_app():
    users = ["alice", "bob", "charlie"]
    actions = ["view_page", "click_button", "submit_form", "download_file"]
    
    while True:
        # Simulate user activity
        user = random.choice(users)
        action = random.choice(actions)
        
        skarv.put(f"user/{user}/action", action)
        
        # Simulate system metrics
        skarv.put("system/performance/cpu", random.uniform(20, 80))
        skarv.put("system/performance/memory", random.uniform(40, 90))
        skarv.put("system/performance/response_time", random.uniform(100, 500))
        
        # Simulate occasional errors
        if random.random() < 0.1:
            skarv.put("system/error/database", "Connection timeout")
        
        time.sleep(2)

print("🌐 Web Application Simulation Started")
simulate_web_app()
```

### Real-time Dashboard

```python
import skarv
import time
import random
from datetime import datetime

# Dashboard components
@skarv.subscribe("dashboard/metrics/*")
def update_metric(sample):
    metric = str(sample.key_expr).split('/')[-1]
    print(f"📊 {metric.upper()}: {sample.value}")

@skarv.subscribe("dashboard/alerts/*")
def handle_alert(sample):
    alert_type = str(sample.key_expr).split('/')[-1]
    print(f"🚨 {alert_type.upper()} ALERT: {sample.value}")

@skarv.subscribe("dashboard/status")
def update_status(sample):
    print(f"🔄 System Status: {sample.value}")

# Data aggregation
@skarv.subscribe("dashboard/metrics/temperature")
def aggregate_temperatures(sample):
    # Get all temperature readings
    all_temps = skarv.get("sensor/*/temperature")
    if all_temps:
        avg_temp = sum(s.value for s in all_temps) / len(all_temps)
        max_temp = max(s.value for s in all_temps)
        min_temp = min(s.value for s in all_temps)
        
        print(f"🌡️  Temp Summary - Avg: {avg_temp:.1f}°C, Max: {max_temp:.1f}°C, Min: {min_temp:.1f}°C")

# Simulate dashboard data
def simulate_dashboard():
    while True:
        # Update metrics
        skarv.put("dashboard/metrics/temperature", random.uniform(18, 28))
        skarv.put("dashboard/metrics/humidity", random.uniform(40, 80))
        skarv.put("dashboard/metrics/pressure", random.uniform(1000, 1020))
        skarv.put("dashboard/metrics/cpu_usage", random.uniform(10, 90))
        
        # Update status
        skarv.put("dashboard/status", f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
        
        # Generate alerts
        if random.random() < 0.05:
            skarv.put("dashboard/alerts/high_temperature", "Temperature above threshold")
        
        if random.random() < 0.03:
            skarv.put("dashboard/alerts/low_pressure", "Pressure below normal range")
        
        time.sleep(3)

print("📈 Real-time Dashboard Started")
simulate_dashboard()
```

## Advanced Examples

### Data Pipeline with Custom Middleware

```python
import skarv
import time
import json

# Custom middleware for data validation and transformation
def validate_sensor_data(value):
    """Validate sensor data structure."""
    if isinstance(value, dict) and 'value' in value and 'timestamp' in value:
        return value
    return None

def add_metadata(value):
    """Add metadata to sensor data."""
    value['processed_at'] = time.time()
    value['version'] = '1.0'
    return value

def convert_units(value):
    """Convert temperature from Celsius to Fahrenheit."""
    if 'value' in value and isinstance(value['value'], (int, float)):
        value['value_f'] = (value['value'] * 9/5) + 32
    return value

# Register custom middleware
skarv.register_middleware("sensor/*", validate_sensor_data)
skarv.register_middleware("sensor/*", add_metadata)
skarv.register_middleware("sensor/*", convert_units)

# Data processing handlers
@skarv.subscribe("sensor/temperature")
def process_temperature(sample):
    data = sample.value
    print(f"🌡️  Temperature: {data['value']}°C ({data['value_f']:.1f}°F)")
    print(f"   Timestamp: {data['timestamp']}")
    print(f"   Processed: {data['processed_at']}")

@skarv.subscribe("sensor/humidity")
def process_humidity(sample):
    data = sample.value
    print(f"💧 Humidity: {data['value']}%")
    print(f"   Timestamp: {data['timestamp']}")

# Simulate sensor data with proper structure
def simulate_structured_sensors():
    while True:
        # Temperature data
        temp_data = {
            'value': 20 + random.uniform(-5, 5),
            'timestamp': time.time()
        }
        skarv.put("sensor/temperature", temp_data)
        
        # Humidity data
        humidity_data = {
            'value': 60 + random.uniform(-10, 10),
            'timestamp': time.time()
        }
        skarv.put("sensor/humidity", humidity_data)
        
        time.sleep(2)

print("🔧 Advanced Data Pipeline Started")
simulate_structured_sensors()
```

### Multi-Service Communication

```python
import skarv
import time
import threading

# Service A: Data Producer
def service_a():
    """Service A produces sensor data."""
    while True:
        skarv.put("service_a/sensor_data", {
            'temperature': 20 + random.uniform(-2, 2),
            'humidity': 60 + random.uniform(-5, 5),
            'timestamp': time.time()
        })
        time.sleep(1)

# Service B: Data Processor
@skarv.subscribe("service_a/sensor_data")
def service_b_processor(sample):
    """Service B processes sensor data."""
    data = sample.value
    processed_data = {
        'original': data,
        'processed_at': time.time(),
        'status': 'processed'
    }
    skarv.put("service_b/processed_data", processed_data)

# Service C: Data Consumer
@skarv.subscribe("service_b/processed_data")
def service_c_consumer(sample):
    """Service C consumes processed data."""
    data = sample.value
    print(f"📦 Service C received: {data['status']}")
    print(f"   Original temp: {data['original']['temperature']:.1f}°C")
    print(f"   Processed at: {data['processed_at']}")

# Service D: Monitoring
@skarv.subscribe("service_*/**")
def service_monitor(sample):
    """Monitor all service communications."""
    service = str(sample.key_expr).split('/')[0]
    print(f"🔍 {service} activity detected")

# Start services
def start_multi_service_system():
    print("🚀 Starting Multi-Service System")
    
    # Start service A in a separate thread
    service_a_thread = threading.Thread(target=service_a, daemon=True)
    service_a_thread.start()
    
    # Main thread continues to handle other services
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("🛑 Stopping Multi-Service System")

start_multi_service_system()
```

## Performance Examples

### High-Frequency Data Processing

```python
import skarv
from skarv.middlewares import throttle, batch
import time
import threading

# Set up high-frequency data processing
skarv.register_middleware("high_freq/data", throttle(0.1))  # Max 10 updates/sec
skarv.register_middleware("high_freq/data", batch(100))     # Batch 100 readings

# Data handlers
@skarv.subscribe("high_freq/data")
def handle_batched_data(sample):
    print(f"📊 Received batch of {len(sample.value)} readings")
    avg_value = sum(sample.value) / len(sample.value)
    print(f"   Average: {avg_value:.2f}")

# High-frequency data producer
def high_frequency_producer():
    """Produce data at high frequency."""
    counter = 0
    while True:
        skarv.put("high_freq/data", counter)
        counter += 1
        time.sleep(0.01)  # 100 Hz

# Performance monitoring
@skarv.subscribe("high_freq/performance")
def monitor_performance(sample):
    print(f"⚡ Performance: {sample.value}")

# Start high-frequency processing
def start_high_frequency_system():
    print("⚡ Starting High-Frequency Data Processing")
    
    # Start producer in separate thread
    producer_thread = threading.Thread(target=high_frequency_producer, daemon=True)
    producer_thread.start()
    
    # Monitor performance
    start_time = time.time()
    while True:
        elapsed = time.time() - start_time
        skarv.put("high_freq/performance", f"Running for {elapsed:.1f}s")
        time.sleep(5)

start_high_frequency_system()
```

## Next Steps

- [API Reference](../api/core.md) - Complete API documentation
- [Key Expressions](key-expressions.md) - Learn about pattern matching
- [Middleware](middleware.md) - Transform data with middleware 