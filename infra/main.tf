# Copyright (c) HashiCorp, Inc.
# SPDX-License-Identifier: MPL-2.0

terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "3.67.0"
    }
    hcp = {
      source = "hashicorp/hcp"
      version = "~>0.91.0"
    }
  }

  cloud {
    organization = "timkrebs9"
    
    workspaces {
      name = "llm-chat-api"
    }
  }
}

#provider "hcp" {
#  # Configuration using environment variables
#  # HCP_CLIENT_ID and HCP_CLIENT_SECRET should be set in Terraform Cloud workspace
#}

data "hcp_vault_secrets_app" "azure_sp" {
  app_name = "azure-sp-secrets"
}

provider "azurerm" {
  features {}
  skip_provider_registration = true

  subscription_id   = data.hcp_vault_secrets_app.azure_sp.secrets["subscription_id"]
  tenant_id         = data.hcp_vault_secrets_app.azure_sp.secrets["tenant_id"]
  client_id         = data.hcp_vault_secrets_app.azure_sp.secrets["client_id"]
  client_secret     = data.hcp_vault_secrets_app.azure_sp.secrets["client_secret"]
}
