variable "location" {
  type    = string
  default = "southeastasia"
}

variable "rg_name" {
  type    = string
  default = "Cloud_Project"
}

variable "acr_name" {
  type    = string
  description = "Name for ACR (must be globally unique)"
  default = "healthchatbot" # change to unique name
}

variable "aks_name" {
  type    = string
  default = "mentalhealthchatbot"
}

variable "node_count" {
  type    = number
  default = 1
}

variable "node_vm_size" {
  type    = string
  default = "Standard_DS2_v2"
}
