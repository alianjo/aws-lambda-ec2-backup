output "lambda_function_arn" {
  value = aws_lambda_function.ec2_backup.arn
}

output "eventbridge_rule_arn" {
  value = aws_cloudwatch_event_rule.schedule.arn
}

output "iam_role_arn" {
  value = aws_iam_role.lambda_exec.arn
}