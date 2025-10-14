import logging
from botocore.exceptions import ClientError

def log_error(logger, error, context=None):
    """Log an error with optional context."""
    error_message = str(error)
    if context:
        error_message = f"{context}: {error_message}"
    logger.error(error_message, exc_info=True)
    return error_message

def format_response(status_code, body):
    """Format a consistent API response."""
    if isinstance(body, str):
        body = {'message': body}
    
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(body, default=str)
    }

def create_tags(resource_ids, tags):
    """Create or update tags for AWS resources."""
    if not resource_ids or not tags:
        return False
        
    if not isinstance(resource_ids, list):
        resource_ids = [resource_ids]
        
    if not all(isinstance(rid, str) for rid in resource_ids):
        raise ValueError("All resource IDs must be strings")
        
    if not isinstance(tags, dict):
        raise ValueError("Tags must be a dictionary")
        
    ec2 = boto3.client('ec2')
    tag_list = [{'Key': k, 'Value': v} for k, v in tags.items()]
    
    try:
        ec2.create_tags(Resources=resource_ids, Tags=tag_list)
        return True
    except ClientError as e:
        log_error(logging.getLogger(), f"Error creating tags: {str(e)}")
        return False

def get_ssm_parameter(name, decrypt=True):
    """Get a parameter from AWS Systems Manager Parameter Store."""
    ssm = boto3.client('ssm')
    try:
        response = ssm.get_parameter(Name=name, WithDecryption=decrypt)
        return response['Parameter']['Value']
    except ssm.exceptions.ParameterNotFound:
        return None
    except Exception as e:
        log_error(logging.getLogger(), f"Error getting SSM parameter {name}: {str(e)}")
        raise

def send_sns_notification(topic_arn, subject, message):
    """Send a notification via Amazon SNS."""
    sns = boto3.client('sns')
    try:
        sns.publish(
            TopicArn=topic_arn,
            Subject=str(subject)[:100],  # SNS subject has 100 char limit
            Message=json.dumps({'default': json.dumps(message, indent=2)}),
            MessageStructure='json'
        )
        return True
    except Exception as e:
        log_error(logging.getLogger(), f"Error sending SNS notification: {str(e)}")
        return False