variable "project_name" {
  description = "Globally unique lowercase project prefix."
  type        = string
  default     = "risk-intelligence"
}

variable "storage_prefix" {
  description = "Lowercase alphanumeric prefix for the ADLS account."
  type        = string
  default     = "risklake"
}

variable "location" {
  description = "Azure region for the platform."
  type        = string
  default     = "East US 2"
}

variable "databricks_sku" {
  description = "Databricks pricing tier."
  type        = string
  default     = "premium"
}

variable "tags" {
  description = "Governance tags applied to all resources."
  type        = map(string)
  default = {
    platform   = "predictive-risk-intelligence"
    owner      = "data-platform"
    costCenter = "risk-analytics"
    managedBy  = "terraform"
  }
}
