# Predictive Risk Intelligence Platform — Ledger & Lattice architecture
terraform {
  required_version = ">= 1.6.0"
  required_providers {
    azurerm = { source = "hashicorp/azurerm", version = "~> 4.0" }
    random  = { source = "hashicorp/random", version = "~> 3.6" }
  }
}

provider "azurerm" { features {} }

resource "random_string" "suffix" {
  length = 6
  special = false
  upper = false
}

resource "azurerm_resource_group" "platform" {
  name     = "${var.project_name}-rg"
  location = var.location
  tags     = var.tags
}

resource "azurerm_storage_account" "adls" {
  name                     = "${var.storage_prefix}${random_string.suffix.result}"
  resource_group_name      = azurerm_resource_group.platform.name
  location                 = azurerm_resource_group.platform.location
  account_tier             = "Standard"
  account_replication_type = "ZRS"
  is_hns_enabled           = true
  min_tls_version          = "TLS1_2"
  tags                     = var.tags
}

resource "azurerm_storage_data_lake_gen2_filesystem" "lake" {
  name               = "risk-lake"
  storage_account_id = azurerm_storage_account.adls.id
}

resource "azurerm_data_factory" "adf" {
  name                = "${var.project_name}-adf"
  location            = azurerm_resource_group.platform.location
  resource_group_name = azurerm_resource_group.platform.name
  identity { type = "SystemAssigned" }
  tags = var.tags
}

resource "azurerm_databricks_workspace" "workspace" {
  name                = "${var.project_name}-dbx"
  resource_group_name = azurerm_resource_group.platform.name
  location            = azurerm_resource_group.platform.location
  sku                 = var.databricks_sku
  managed_resource_group_name = "${var.project_name}-dbx-managed"
  tags = var.tags
}

resource "azurerm_machine_learning_workspace" "ml" {
  name                    = "${var.project_name}-mlw"
  location                = azurerm_resource_group.platform.location
  resource_group_name     = azurerm_resource_group.platform.name
  application_insights_id = azurerm_application_insights.ml.id
  key_vault_id            = azurerm_key_vault.ml.id
  storage_account_id      = azurerm_storage_account.adls.id
  identity { type = "SystemAssigned" }
  tags = var.tags
}

resource "azurerm_application_insights" "ml" {
  name                = "${var.project_name}-appi"
  location            = azurerm_resource_group.platform.location
  resource_group_name = azurerm_resource_group.platform.name
  application_type    = "web"
  tags = var.tags
}

resource "azurerm_key_vault" "ml" {
  name                       = "${var.project_name}-kv-${random_string.suffix.result}"
  location                   = azurerm_resource_group.platform.location
  resource_group_name        = azurerm_resource_group.platform.name
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  sku_name                   = "standard"
  purge_protection_enabled   = true
  soft_delete_retention_days = 7
  tags = var.tags
}

data "azurerm_client_config" "current" {}

output "resource_group_name" { value = azurerm_resource_group.platform.name }
output "adls_endpoint" { value = azurerm_storage_account.adls.primary_dfs_endpoint }
output "databricks_workspace_url" { value = azurerm_databricks_workspace.workspace.workspace_url }
output "ml_workspace_name" { value = azurerm_machine_learning_workspace.ml.name }
