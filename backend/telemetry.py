import os
from dataclasses import dataclass

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.http.metric_exporter import (
    OTLPMetricExporter,
)
from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


@dataclass(frozen=True)
class TelemetryProviders:
    tracer_provider: TracerProvider
    meter_provider: MeterProvider

    def shutdown(self) -> None:
        """Flush buffered telemetry and stop exporter workers."""
        self.meter_provider.shutdown()
        self.tracer_provider.shutdown()


_providers: TelemetryProviders | None = None


def configure_telemetry() -> TelemetryProviders:
    """Configure the application's OpenTelemetry providers once."""
    global _providers

    if _providers is not None:
        return _providers

    resource = Resource.create(
        {
            "service.name": os.getenv(
                "OTEL_SERVICE_NAME",
                "authentication-api",
            ),
            "service.version": os.getenv(
                "APP_VERSION",
                "development",
            ),
            "deployment.environment.name": os.getenv(
                "APP_ENV",
                "development",
            ),
        }
    )

    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter())
    ) # converts traces to OpenTel protocol
    trace.set_tracer_provider(tracer_provider)

    metric_reader = PeriodicExportingMetricReader(
        OTLPMetricExporter()
    )
    meter_provider = MeterProvider(
        resource=resource,
        metric_readers=[metric_reader],
    )
    metrics.set_meter_provider(meter_provider)

    _providers = TelemetryProviders(
        tracer_provider=tracer_provider,
        meter_provider=meter_provider,
    )
    return _providers