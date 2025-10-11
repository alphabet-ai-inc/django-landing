module "linode_instances" {
#   source = "git::https://github.com/alphabet-ai-inc/linode-instances-module.git?ref=main"
  source = "git::https://github.com/SergueiMoscow/linode-instances-module.git?ref=main"

  server_group_name = var.server_group_name
  app              = var.app
  bucket_name = var.bucket_name
  bucket_region = var.bucket_region
  image_id = var.image_id
  infra_backend_state_key = var.infra_backend_state_key
  github_token_vault_path = var.github_token_vault_path
  env = var.env
  node_name_prefix = var.node_name_prefix
}

data "vault_generic_secret" "github_token" {
  path = var.github_token_vault_path
}

locals {
  tokens = fileexists("~/.vault_tokens") ? yamldecode(file("~/.vault_tokens"))["tokens"] : {}
}
