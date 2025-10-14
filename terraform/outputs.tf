output "lambda_function_arn" {
  value = aws_lambda_function.ec2_backup_function.arn
}

output "eventbridge_rule_arn" {
  value = aws_cloudwatch_event_rule.ec2_backup_schedule.arn
}

output "iam_role_arn" {
  value = aws_iam_role.lambda_execution_role.arn
}