import boto3
import os
import logging
from datetime import datetime, timedelta
from botocore.exceptions import ClientError
from utils import log_error, format_response, create_tags

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Main Lambda handler for EC2 backup operations.
    
    Expected event format:
    {
        "action": "backup" | "cleanup",
        "instance_tags": {"Key": "Value", ...},  # Optional: filter instances by tags
        "retention_days": 30,  # Optional: override default retention
        "description": "Custom description"  # Optional: custom snapshot description
    }
    """
    try:
        action = event.get('action', 'backup')
        instance_tags = event.get('instance_tags', {})
        retention_days = int(event.get('retention_days', os.environ.get('SNAPSHOT_RETENTION_DAYS', '30')))
        
        if action == 'backup':
            return create_backups(instance_tags, event.get('description', 'Automated backup'))
        elif action == 'cleanup':
            return cleanup_old_snapshots(retention_days, instance_tags)
        else:
            return format_response(400, f"Invalid action: {action}")
    except Exception as e:
        log_error(logger, f"Error in lambda_handler: {str(e)}")
        return format_response(500, f"Error processing request: {str(e)}")

def create_backups(instance_tags, description):
    """Create snapshots for EC2 instances matching the given tags."""
    ec2 = boto3.client('ec2')
    
    # Find instances with matching tags
    filters = [{'Name': f'tag:{k}', 'Values': [v]} for k, v in instance_tags.items()]
    filters.append({'Name': 'instance-state-name', 'Values': ['running', 'stopped']})
    
    try:
        instances = ec2.describe_instances(Filters=filters)['Reservations']
        if not instances:
            return format_response(200, "No instances found matching the criteria.")
            
        created_snapshots = []
        
        for reservation in instances:
            for instance in reservation['Instances']:
                instance_id = instance['InstanceId']
                instance_name = next((tag['Value'] for tag in instance.get('Tags', [])
                                    if tag['Key'] == 'Name'), instance_id)
                
                # Create snapshots for each volume
                for volume in instance.get('BlockDeviceMappings', []):
                    if 'Ebs' in volume:
                        volume_id = volume['Ebs']['VolumeId']
                        snapshot_desc = f"{description} - {instance_name} ({volume_id})"
                        
                        try:
                            snapshot = ec2.create_snapshot(
                                VolumeId=volume_id,
                                Description=snapshot_desc,
                                TagSpecifications=[{
                                    'ResourceType': 'snapshot',
                                    'Tags': [
                                        {'Key': 'Name', 'Value': f"{instance_name}-{volume_id}-{datetime.utcnow().strftime('%Y%m%d%H%M')}"},
                                        {'Key': 'InstanceId', 'Value': instance_id},
                                        {'Key': 'VolumeId', 'Value': volume_id},
                                        {'Key': 'CreatedBy', 'Value': 'lambda-backup'},
                                        {'Key': 'AutoSnapshot', 'Value': 'true'}
                                    ]
                                }]
                            )
                            created_snapshots.append({
                                'InstanceId': instance_id,
                                'VolumeId': volume_id,
                                'SnapshotId': snapshot['SnapshotId']
                            })
                            logger.info(f"Created snapshot {snapshot['SnapshotId']} for volume {volume_id}")
                            
                        except ClientError as e:
                            log_error(logger, f"Error creating snapshot for volume {volume_id}: {str(e)}")
                            continue
                            
        return format_response(200, {
            'message': 'Backup completed',
            'created_snapshots': created_snapshots
        })
        
    except ClientError as e:
        error_msg = f"Error describing instances: {str(e)}"
        log_error(logger, error_msg)
        return format_response(500, error_msg)

def cleanup_old_snapshots(retention_days, instance_tags):
    """Delete snapshots older than retention_days that match the given tags."""
    ec2 = boto3.client('ec2')
    
    # Calculate cutoff date
    cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
    
    # Build filters
    filters = [
        {'Name': 'tag:AutoSnapshot', 'Values': ['true']},
        {'Name': 'tag:CreatedBy', 'Values': ['lambda-backup']},
        {'Name': 'start-time', 'Values': [f"{cutoff_date.strftime('%Y-%m-%d')}T00:00:00.000Z"]},
        {'Name': 'status', 'Values': ['completed']}
    ]
    
    # Add instance tags to filter
    for tag_key, tag_value in instance_tags.items():
        filters.append({'Name': f'tag:{tag_key}', 'Values': [tag_value]})
    
    try:
        # Get all snapshots matching the criteria
        snapshots = []
        paginator = ec2.get_paginator('describe_snapshots')
        for page in paginator.paginate(OwnerIds=['self'], Filters=filters):
            snapshots.extend(page['Snapshots'])
            
        # Filter snapshots older than retention period
        old_snapshots = [
            s for s in snapshots 
            if s['StartTime'].replace(tzinfo=None) < cutoff_date
        ]
        
        # Delete old snapshots
        deleted = []
        for snapshot in old_snapshots:
            try:
                ec2.delete_snapshot(SnapshotId=snapshot['SnapshotId'])
                deleted.append({
                    'SnapshotId': snapshot['SnapshotId'],
                    'VolumeId': snapshot.get('VolumeId'),
                    'StartTime': str(snapshot['StartTime'])
                })
                logger.info(f"Deleted old snapshot: {snapshot['SnapshotId']}")
            except ClientError as e:
                log_error(logger, f"Error deleting snapshot {snapshot['SnapshotId']}: {str(e)}")
                continue
                
        return format_response(200, {
            'message': 'Cleanup completed',
            'deleted_snapshots': deleted,
            'total_deleted': len(deleted)
        })
        
    except ClientError as e:
        error_msg = f"Error during snapshot cleanup: {str(e)}"
        log_error(logger, error_msg)
        return format_response(500, error_msg)