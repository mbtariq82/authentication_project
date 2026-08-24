import logging
import os
from dataclasses import dataclass

from fastapi import FastAPI
from opentelemetry import metrics, trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.http._log_exporter import (
    OTLPLogExporter,
)
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
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
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
    logger_provider: LoggerProvider | None = None
    log_handler: LoggingHandler | None = None

    def shutdown(self) -> None:
        """Flush buffered telemetry and stop exporter workers."""
        if self.log_handler is not None:
            logging.getLogger().removeHandler(self.log_handler)
            logging.getLogger("uvicorn.error").removeHandler(
                self.log_handler
            )
            logging.getLogger("uvicorn.access").removeHandler(
                self.log_handler
            )
        if self.logger_provider is not None:
            self.logger_provider.shutdown()
        self.meter_provider.shutdown()
        self.tracer_provider.shutdown()


_providers: TelemetryProviders | None = None


def _log_server_request(span, scope: dict) -> None:
    """Write a request log while its OpenTelemetry span is active."""
    if span is None or not span.is_recording():
        return

    span_context = span.get_span_context()
    logging.getLogger("uvicorn.error").info(
        "request_started method=%s path=%s trace_id=%032x span_id=%016x",
        scope.get("method", ""),
        scope.get("path", ""),
        span_context.trace_id,
        span_context.span_id,
    )


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

    logger_provider = None
    log_handler = None
    if os.getenv("OTEL_LOGS_EXPORTER", "none").lower() == "otlp":
        logger_provider = LoggerProvider(resource=resource)
        logger_provider.add_log_record_processor(
            BatchLogRecordProcessor(OTLPLogExporter())
        )
        set_logger_provider(logger_provider)

        log_handler = LoggingHandler(
            level=logging.INFO,
            logger_provider=logger_provider,
        )
        logging.getLogger().setLevel(logging.INFO)
        logging.getLogger().addHandler(log_handler)
        logging.getLogger("uvicorn.error").addHandler(log_handler)
        logging.getLogger("uvicorn.access").addHandler(log_handler)

    _providers = TelemetryProviders(
        tracer_provider=tracer_provider,
        meter_provider=meter_provider,
        logger_provider=logger_provider,
        log_handler=log_handler,
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
        server_request_hook=_log_server_request,
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
