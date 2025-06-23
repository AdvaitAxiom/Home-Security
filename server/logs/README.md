# Server Logs Directory

This directory contains log files specific to the Flask server component of the Smart Home Anomaly Detection System.

## Log Files

- `server.log`: Main server log file containing detailed information about server operations, API requests, errors, and debugging information.

## Log Format

The server log uses the following format:

```
[TIMESTAMP] [LEVEL] [MODULE] - Message
```

Where:
- `TIMESTAMP`: Date and time of the log entry (ISO format)
- `LEVEL`: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `MODULE`: The module or component that generated the log
- `Message`: The log message

## Log Levels

- `DEBUG`: Detailed information, typically of interest only when diagnosing problems.
- `INFO`: Confirmation that things are working as expected.
- `WARNING`: An indication that something unexpected happened, or may happen in the near future (e.g. 'disk space low'). The software is still working as expected.
- `ERROR`: Due to a more serious problem, the software has not been able to perform some function.
- `CRITICAL`: A serious error, indicating that the program itself may be unable to continue running.

## Example Log Entries

```
[2023-12-01 08:15:30,123] [INFO] [app] - Server started on 127.0.0.1:5000
[2023-12-01 08:16:45,456] [INFO] [app] - GET /status 200 - 15ms
[2023-12-01 08:17:30,789] [INFO] [app] - GET /analyze 200 - 120ms
[2023-12-01 08:18:10,321] [ERROR] [app] - Failed to fetch data from ThingSpeak: Connection timeout
[2023-12-01 08:20:05,654] [INFO] [app] - POST /simulate 200 - 85ms
```

## Log Management

Log files are not automatically rotated. For production use, consider implementing log rotation using a tool like `logrotate` on Linux or a similar utility on your operating system.