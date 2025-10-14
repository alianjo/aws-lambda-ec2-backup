variable "aws_region" {
  description = "The AWS region where the resources will be deployed"
  type        = string
  default     = "us-east-1"
}

variable "lambda_function_name" {
  description = "The name of the AWS Lambda function"
  type        = string
  default     = "ec2-backup-lambda"
}

variable "snapshot_retention_days" {
  description = "The number of days to retain EC2 snapshots"
  type        = number
  default     = 30
}

variable "eventbridge_rule_schedule" {
  description = "The schedule expression for the EventBridge rule (e.g., rate(1 day))"
  type        = string
  default     = "rate(1 day)"
}