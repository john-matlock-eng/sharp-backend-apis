output "api_gateway_url" {
  description = "URL of the deployed API Gateway"
  value       = module.api_deployment.api_gateway_url
}
