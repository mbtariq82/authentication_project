resource "aws_cloudwatch_log_group" "telemetry_metrics" {
  name              = "/authentication-project/metrics"
  log_group_class   = "STANDARD"
  retention_in_days = 30

  tags = {
    Name = "authentication-project-telemetry-metrics"
  }
}
