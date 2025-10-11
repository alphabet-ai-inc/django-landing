terraform {
  required_providers {
    linode = {
      source  = "linode/linode"
      version = "3.4.0"
    }
    # Set GitHub provider
    github = {
      source  = "integrations/github"
      version = "~> 6.0"
    }

  }
  backend "s3" {
    skip_credentials_validation = true
    skip_region_validation      = true
    skip_requesting_account_id  = true
    skip_metadata_api_check     = true
    skip_s3_checksum            = true
    shared_credentials_files    = ["~/.linode_credentials"]
    shared_config_files         = ["~/.linode_config"]
    profile                     = "linode"
    bucket                      = "infra-config"
    key                         = "states/instances/dev/tfstate"
    region                      = "us-ord"
    endpoints = {
      s3 = "https://us-ord-1.linodeobjects.com"
    }
  }
}

provider "linode" {
  token = trimspace(file("~/.linode_token"))
}

provider "github" {
  token = data.vault_generic_secret.github_token.data["token"]
  owner = var.github_owner
}

provider "vault" {
  address          = var.vault_url
  token            = local.tokens[var.env][var.server_group_name]
  skip_child_token = true
}