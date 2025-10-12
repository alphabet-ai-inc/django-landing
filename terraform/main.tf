module "linode_instances" {
#   source = "git::https://github.com/alphabet-ai-inc/linode-instances-module.git?ref=main"
  source = "git::https://github.com/SergueiMoscow/linode-instances-module.git?ref=main"

  server_group_name = var.server_group_name
  app              = var.app
  node_count = var.node_count
  bucket_name = var.bucket_name
  bucket_region = var.bucket_region
  image_id = var.image_id
  infra_backend_state_key = var.infra_backend_state_key
  github_token_vault_path = var.github_token_vault_path
  env = var.env
  node_name_prefix = var.node_name_prefix
}

module "linode_domain" {
  source        = "git::https://github.com/alphabet-ai-inc/linode-subdomain-module.git?ref=main"
  domain_name   = var.domain_name
  domain_prefix = var.domain_prefix
  domain_ip     = length(module.linode_instances.instance_ips) > 0 ? module.linode_instances.instance_ips[0] : ""
}

data "vault_generic_secret" "github_token" {
  path = var.github_token_vault_path
}

locals {
  tokens = fileexists("~/.vault_tokens") ? yamldecode(file("~/.vault_tokens"))["tokens"] : {}
}
