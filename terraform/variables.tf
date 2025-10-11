variable "node_name_prefix" {
  description = "Prefix for Linode instance names"
  type        = string
  default     = "app-node"
}

variable "instance_type" {
  description = "Linode instance type"
  type        = string
  default     = "g6-nanode-1"
}

variable "node_count" {
  description = "Number of Linode instances to create"
  type        = number
  default     = 2
}

variable "image_id" {
  description = "Image ID"
  type        = string
}

variable "region" {
  type    = string
  default = "us-ord"
}

variable "infra_backend_state_key" {
  type = string
}

variable "git_repositories" {
  description = "URL list with Git-repositories"
  type        = list(string)
  default     = []
}

variable "ssh_pub_key_file" {
  type    = string
  default = "~/.ssh/id_ed25519.pub"
}

variable "authorized_users" {
  type    = list(string)
  default = []
}

variable "app" {
  description = "List of applications to deploy"
  type = list(object({
    name      = string
    url       = string
    directory = string
    commands  = list(string)
  }))
}

variable "env" {
  description = "Environment (dev, test, prod)"
  type        = string
  default     = "dev"
  validation {
    condition     = contains(["dev", "test", "prod"], var.env)
    error_message = "Environment must be 'dev', 'test', or 'prod'."
  }
}

variable "bucket_name" {
  description = "Name of the Object Storage bucket"
  type        = string
}

variable "bucket_region" {
  description = "Not all VPC regions work with Objects Storages"
  type        = string
}

variable "ssh_user" {
  description = "SSH user for deployment"
  type        = string
  default     = "deploy"
}

variable "github_owner" {
  description = "Github organization"
  type        = string
  default     = ""
}

variable "github_token_vault_path" {
  description = "Vault path for GitHub token"
  type        = string
  default     = "secret/github/github_token"
}

variable "server_group_name" {
  description = "Name of the server group (e.g., 'authserver_dev', 'payment_prod')"
  type        = string
}

variable "vault_url" {
  type    = string
  default = "https://vault.sushkovs.ru"
}
