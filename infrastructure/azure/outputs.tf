output "resource_group_name" {
  value = azurerm_resource_group.main.name
}

output "fastapi_public_ip" {
  value = azurerm_public_ip.fastapi.ip_address
}

output "fastapi_url" {
  value = "http://${azurerm_public_ip.fastapi.ip_address}:8000"
}

output "postgres_fqdn" {
  value = azurerm_postgresql_flexible_server.main.fqdn
}
