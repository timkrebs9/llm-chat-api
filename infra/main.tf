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
      version = "~=0.91.0
    }
  }

  required_version = ">= 0.14"
}

