# Django Landing Pages

### Pass .env to vault:
#### Generate dev_env.json from dev.env
```shell
grep -v '^\s*#' dev.env | grep -v '^\s*$' | sed 's/^\s*//; s/\s*$//; s/^/"/; s/=/": "/; s/$/",/' | tr -d '\n' | sed 's/,$//' | sed 's/^/{"data": {/; s/$/}}/' > dev_env.json
```


### Upload dev_env.json to vault (change <token> with your token, <url> with your url:
```shell
curl \
  --header "X-Vault-Token: <token>" \
  --request POST \
  --data @dev_env.json \
  https://<url>/v1/secret/data/django_landing/dev
```

### Run Caddy
check:
```shell
dig +short landing_dev.aztech-ai.com
```
run:
```shell
export DOMAIN=landing_dev.aztech-ai.com
export VM_IP=172.239.39.13
./run_caddy
```