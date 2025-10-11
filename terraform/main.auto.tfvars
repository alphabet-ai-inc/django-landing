node_count              = 1
node_name_prefix        = "worker-node"
image_id                = "linode/ubuntu24.04"
region                  = "us-ord"
infra_backend_state_key = "states/infra/dev/tfstate"
authorized_users        = ["jpassano", "ssouchkov"]
server_group_name       = "landing_dev"
env                     = "dev"

app = [
  {
    name      = "django_landing"
    url       = "https://github.com/SergueiMoscow/django-landing"
    directory = "/app/django-landing"
    commands  = [
      "git checkout main",
      "until docker compose up -d; do sleep 2; done",
      "timeout 60 bash -c 'while ! nc -z localhost 8000; do sleep 1; done'"
    ]
  }
]

bucket_name             = "infra-config"
bucket_region           = "us-ord"
vault_url               = "https://vault.sushkovs.ru"
github_token_vault_path = "secret/github/github_token"
github_owner            = "alphabet-ai-inc"

