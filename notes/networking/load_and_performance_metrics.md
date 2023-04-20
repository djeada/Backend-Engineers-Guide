## Load and Performance Metrics

When designing and evaluating a system, it's important to understand performance characteristics and potential bottlenecks. Choose appropriate metrics based on system requirements and characteristics.

### Throughput

- Measures records or requests processed per second.
- Useful for batch jobs or high-volume request systems.
- Measured in requests per second (RPS) or records per second (RPS).

### Response Time

- Time between a client sending a request and receiving a response.
- Important for online systems where low latency matters.
- Measured in milliseconds (ms) or seconds (s).

### Latency

- Duration a request spends waiting to be handled.
- Affected by factors like network latency, server processing time, and database query time.
- Measured in milliseconds (ms) or seconds (s).

### Tail Latency

- Latency at a certain percentile of requests (e.g., p95).
- Indicates the presence of outliers or bottlenecks affecting user experience.
- Measured in milliseconds (ms) or seconds (s).

### Other Metrics

- Error rate: Percentage or ratio of requests resulting in an error.
- CPU utilization: Percentage of CPU usage by the system.
- Memory usage: Amount of memory used by the system.
- Disk I/O: Rate of data read and written to disk.
- Network traffic: Rate of data transferred over the network.
- These additional metrics help identify performance bottlenecks and areas for improvement.
