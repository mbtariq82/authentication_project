import os
from dataclasses import dataclass

from fastapi import FastAPI
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
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine


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
    )
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


def instrument_application(
    app: FastAPI,
    engine: AsyncEngine,
    redis_client: Redis,
    providers: TelemetryProviders,
) -> None:
    """Instrument inbound HTTP, PostgreSQL, and Redis operations."""
    FastAPIInstrumentor.instrument_app(
        app,
        tracer_provider=providers.tracer_provider,
        meter_provider=providers.meter_provider,
        excluded_urls=r".*/health",
        exclude_spans=["receive", "send"],
    )
    SQLAlchemyInstrumentor().instrument(
        engine=engine.sync_engine,
        tracer_provider=providers.tracer_provider,
        meter_provider=providers.meter_provider,
    )
    RedisInstrumentor.instrument_client(
        client=redis_client,
        tracer_provider=providers.tracer_provider,
    )
