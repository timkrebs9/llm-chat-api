
data "hcp_vault_secrets_app" "device-registry" {
  app_name = "device-registry"
}

resource "azurerm_postgresql_flexible_server" "device_registry_db" {
  name                   = "device-registry-db"
  resource_group_name    = azurerm_resource_group.default.name
  location               = azurerm_resource_group.default.location
  sku_name               = "GP_Standard_D2s_v3"
  storage_mb             = 32768
  backup_retention_days  = 7
  geo_redundant_backup_enabled = false
  administrator_login    = "adminuser"
  administrator_password = data.hcp_vault_secrets_app.device-registry.secrets["db_password"]
  version                = "12"
  zone                   = "1"
}

resource "azurerm_postgresql_flexible_server_firewall_rule" "allow_all" {
  name                = "allow-all"
  server_id = azurerm_postgresql_flexible_server.device_registry_db.id
  start_ip_address    = "0.0.0.0"
  end_ip_address      = "255.255.255.255"
}

output "db_connection_string" {
  value       = "postgres://adminuser:${data.hcp_vault_secrets_app.device-registry.secrets["db_password"]}@${azurerm_postgresql_flexible_server.device_registry_db.fqdn}:5432/device_registry"
  sensitive   = true
}