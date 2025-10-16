output "domain" {
  value = module.linode_domain.domain_name
}

output "ips" {
  description = "IP addresses of the created Linode instances"
  value       = module.linode_instances.instance_ips
}