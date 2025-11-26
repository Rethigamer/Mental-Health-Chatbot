resource "azurerm_resource_group" "rg" {
  name     = var.rg_name
  location = var.location

  tags = {
    environment = "development"
    project     = "Cloud-Computing-Project"
  }
}

resource "azurerm_container_registry" "acr" {
  name                = "healthchatbot"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "Basic"
  admin_enabled       = true

  depends_on = [
    azurerm_resource_group.rg
  ]

  tags = {
    environment = "development"
    project     = "Cloud-Computing-Project"
  }
}

resource "azurerm_kubernetes_cluster" "aks" {
  name                = "mentalhealthchatbot"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  dns_prefix          = "mentalhealthchatbot-dns"

  default_node_pool {
    name       = "agentpool"
    node_count = 1
    vm_size    = "Standard_B2s"
  }

  identity {
    type = "SystemAssigned"
  }

  sku_tier = "Free"

  tags = {
    environment = "development"
    project     = "Cloud-Computing-Project"
  }
}

output "resource_group" {
  value = azurerm_resource_group.rg.name
}

output "acr_login_server" {
  value = azurerm_container_registry.acr.login_server
}

output "aks_name" {
  value = azurerm_kubernetes_cluster.aks.name
}

output "kube_config" {
  value     = azurerm_kubernetes_cluster.aks.kube_config_raw
  sensitive = true
}
