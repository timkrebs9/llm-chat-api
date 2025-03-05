resource "azurerm_container_registry" "acr" {
  name                = "${replace(random_pet.prefix.id, "-", "")}acr"
  resource_group_name = azurerm_resource_group.default.name
  location            = azurerm_resource_group.default.location
  sku                 = "Standard"
  admin_enabled       = true

  tags = {
    environment = "Dev"
    managed_by  = "Terraform"
  }
}