# Copyright (c) HashiCorp, Inc.
# SPDX-License-Identifier: MPL-2.0

output "resource_group_name" {
  value = azurerm_resource_group.default.name
}

output "kubernetes_cluster_name" {
  value = azurerm_kubernetes_cluster.default.name
}

# ACR outputs
output "acr_name" {
  value       = azurerm_container_registry.acr.name
  description = "The name of the Azure Container Registry"
}

output "acr_login_server" {
  value       = azurerm_container_registry.acr.login_server
  description = "The login server URL for the Azure Container Registry"
}

output "acr_admin_username" {
  value       = azurerm_container_registry.acr.admin_username
  description = "The admin username for the Azure Container Registry"
  sensitive   = true
}

output "acr_id" {
  value       = azurerm_container_registry.acr.id
  description = "The ID of the Azure Container Registry"
}

output "acr_resource_group" {
  value       = azurerm_container_registry.acr.resource_group_name
  description = "The resource group containing the Azure Container Registry"
}

# AKS outputs
output "host" {
  value     = azurerm_kubernetes_cluster.default.kube_config.0.host
  sensitive = true
}

output "client_certificate" {
  value     = base64decode(azurerm_kubernetes_cluster.default.kube_config.0.client_certificate)
  sensitive = true
}

output "client_key" {
  value     = base64decode(azurerm_kubernetes_cluster.default.kube_config.0.client_key)
  sensitive = true
}

output "cluster_ca_certificate" {
  value     = base64decode(azurerm_kubernetes_cluster.default.kube_config.0.cluster_ca_certificate)
  sensitive = true
}

output "kube_config" {
  value     = azurerm_kubernetes_cluster.default.kube_config_raw
  sensitive = true
}

# output "cluster_username" {
#   value = azurerm_kubernetes_cluster.default.kube_config.0.username
# }

# output "cluster_password" {
#   value = azurerm_kubernetes_cluster.default.kube_config.0.password
# }
