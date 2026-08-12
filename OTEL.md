# OpenTelemetry Implementation Notes

These notes explain the OpenTelemetry integration in this project and the
reasoning behind the implementation choices.

## Project telemetry flow

```text
HTTP request
    -> Uvicorn
    -> FastAPI / ASGI
    -> service code
    -> SQLAlchemy and/or Redis
    -> OpenTelemetry spans and measurements
    -> OTLP exporters
    -> OpenTelemetry Collector (next implementation step)
    -> observability backend such as X-Ray or CloudWatch
```

OpenTelemetry creates and exports telemetry. It does not store traces or
provide dashboards by itself.

## Trace provider configuration, line by line
Trace pipeline:
Tracer → spans → TracerProvider → BatchSpanProcessor
       → OTLPSpanExporter → Collector

The trace configuration is:

```python
tracer_provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter())
)
trace.set_tracer_provider(tracer_provider)
```

### `OTLPSpanExporter()`

```python
OTLPSpanExporter()
```

This constructs an exporter for trace spans. It serializes completed spans
using OTLP, the OpenTelemetry Protocol, and sends them using HTTP/protobuf.

The exporter reads standard environment configuration, including:

```text
OTEL_EXPORTER_OTLP_ENDPOINT
OTEL_EXPORTER_OTLP_TRACES_ENDPOINT
OTEL_EXPORTER_OTLP_HEADERS
OTEL_EXPORTER_OTLP_TIMEOUT
```

The exporter is a sender. It does not create spans, store them permanently, or
display them.

### `BatchSpanProcessor(...)`

```python
BatchSpanProcessor(OTLPSpanExporter())
```

This creates a span processor and gives it the exporter it should use.

When a span ends, the batch processor normally places it into an in-memory
queue. A background worker exports groups of spans together. This avoids making
an OTLP network request directly in the request-handling path for every span.

The processor is also responsible for flushing its queue during shutdown.

### `tracer_provider.add_span_processor(...)`

```python
tracer_provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter())
)
```

This registers the batch processor with the application's `TracerProvider`.
The nested expressions are evaluated from the inside out:

1. Construct an `OTLPSpanExporter`.
2. Construct a `BatchSpanProcessor` that uses that exporter.
3. Register the processor with `tracer_provider`.

After registration, spans created through this provider are passed to the
processor when they finish.

### `trace.set_tracer_provider(tracer_provider)`

```python
trace.set_tracer_provider(tracer_provider)
```

This installs the provider as the process-wide OpenTelemetry trace provider.
Code can then use:

```python
tracer = trace.get_tracer(__name__)
```

and receive a tracer backed by this configuration.

The FastAPI, SQLAlchemy, and Redis instrumentors currently receive the provider
explicitly as well. Setting the global provider is still useful for future
manual spans and for libraries that obtain their tracer through the global
OpenTelemetry API.

## Metric provider configuration, line by line
Metric pipeline:
Meter → counters/histograms → MeterProvider
      → PeriodicExportingMetricReader
      → OTLPMetricExporter → Collector

The metric configuration is:

```python
metric_reader = PeriodicExportingMetricReader(
    OTLPMetricExporter()
)
meter_provider = MeterProvider(
    resource=resource,
    metric_readers=[metric_reader],
)
metrics.set_meter_provider(meter_provider)
```

### `OTLPMetricExporter()`

```python
OTLPMetricExporter()
```

This constructs the OTLP exporter for metrics. It serializes collected metric
data and sends it to the configured OTLP endpoint using HTTP/protobuf.

It reads standard environment configuration such as:

```text
OTEL_EXPORTER_OTLP_ENDPOINT
OTEL_EXPORTER_OTLP_METRICS_ENDPOINT
OTEL_EXPORTER_OTLP_HEADERS
OTEL_EXPORTER_OTLP_TIMEOUT
```

### `PeriodicExportingMetricReader(...)`

```python
metric_reader = PeriodicExportingMetricReader(
    OTLPMetricExporter()
)
```

Metrics differ from spans. A span has a definite end, but a counter or
histogram can receive measurements throughout the process lifetime. Something
must periodically collect a snapshot of the aggregated metric state.

This line performs two operations:

1. Construct an `OTLPMetricExporter`.
2. Construct a reader that periodically collects metrics and gives each
   collection to that exporter.

The collection interval can be configured with:

```text
OTEL_METRIC_EXPORT_INTERVAL
```

### `MeterProvider(...)`

```python
meter_provider = MeterProvider(
    resource=resource,
    metric_readers=[metric_reader],
)
```

This creates the application's main metrics configuration.

`resource=resource` attaches the same service identity to metrics that is
attached to traces, for example:

```text
service.name=authentication-api
service.version=<application version>
deployment.environment.name=development
```

`metric_readers=[metric_reader]` connects the provider to the periodic reader.
The argument is a list because a provider can have more than one reader, with
different export or collection behaviour.

The provider supplies `Meter` objects. A meter can create metric instruments:

```python
meter = metrics.get_meter(__name__)
login_attempts = meter.create_counter("auth.login.attempts")
```

### `metrics.set_meter_provider(meter_provider)`

```python
metrics.set_meter_provider(meter_provider)
```

This installs the provider as the process-wide OpenTelemetry meter provider.
Calls to `metrics.get_meter(...)` then use this configuration.

## Why traces use a processor but metrics use a reader

Trace spans are discrete objects with a completion event:

```text
start span -> perform operation -> end span -> process completed span
```

Metrics are measurements aggregated over time:

```text
record values repeatedly -> periodically collect aggregation -> export
```

Therefore:

- `BatchSpanProcessor` reacts to completed spans and batches them.
- `PeriodicExportingMetricReader` periodically collects current metric data.

Both eventually pass data to an OTLP exporter.

## Current implementation status

Completed:

- Pinned OpenTelemetry Python dependencies.
- Configured trace and metric providers.
- Configured OTLP/HTTP trace and metric exporters.
- Instrumented FastAPI.
- Instrumented async SQLAlchemy through `engine.sync_engine`.
- Instrumented the async Redis client for traces.
- Excluded `/health` from traces.
- Excluded low-level ASGI `receive` and `send` spans.
- Shut down telemetry providers during application shutdown.

Next:

- Add a local OpenTelemetry Collector with a debug exporter.
- Point the application at it with `OTEL_EXPORTER_OTLP_ENDPOINT`.
- Inspect a real login or user lookup trace.
- Dispose of the SQLAlchemy engine during graceful shutdown.
- Add useful low-cardinality business metrics.
- Later export production traces and metrics to AWS.
