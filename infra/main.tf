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

  #cloud { 
  #  organization = "timkrebs9" 
  #  workspaces { 
  #    name = "llm-chat-api" 
  #  } 
  #}
#
  #required_version = ">= 0.14"
}

#provider "hcp" {
#  # Configuration using environment variables
#  # HCP_CLIENT_ID and HCP_CLIENT_SECRET should be set in Terraform Cloud workspace
#}

provider "azurerm" {
  features {}
  skip_provider_registration = true
}
