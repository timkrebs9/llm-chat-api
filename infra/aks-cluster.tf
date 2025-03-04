# Copyright (c) HashiCorp, Inc.
# SPDX-License-Identifier: MPL-2.0

resource "random_pet" "prefix" {}

data "hcp_vault_secrets_app" "aks_sp" {
  app_name = "aks-sp-secrets"
}

resource "azurerm_resource_group" "default" {
  name     = "${random_pet.prefix.id}-rg"
  location = "West US 2"

  tags = {
    environment = "Dev"
  }
}

resource "azurerm_kubernetes_cluster" "default" {
  name                = "${random_pet.prefix.id}-aks"
  location            = azurerm_resource_group.default.location
  resource_group_name = azurerm_resource_group.default.name
  dns_prefix          = "${random_pet.prefix.id}-k8s"
  kubernetes_version  = "1.30.9"

  default_node_pool {
    name            = "default"
    node_count      = 2
    vm_size         = "Standard_D2_v2"
    os_disk_size_gb = 30
  }

  service_principal {
    client_id     = data.hcp_vault_secrets_app.aks_sp.secrets["appId"]
    client_secret = data.hcp_vault_secrets_app.aks_sp.secrets["password"]
  }

  role_based_access_control_enabled = true

  tags = {
    environment = "Dev"
  }
}
