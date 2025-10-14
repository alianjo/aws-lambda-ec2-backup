# aws-lambda-ec2-backup

A serverless AWS backup automation system using Lambda and EventBridge. Automatically creates and cleans up EC2 volume snapshots on a schedule built with Terraform.

## Table of Contents

- [Overview](#overview)
- [Setup](#setup)
- [Usage](#usage)
- [CI/CD](#cicd)
- [Contributing](#contributing)
- [License](#license)
- [Changelog](#changelog)

## Overview

This project automates the creation and management of EC2 volume snapshots using AWS Lambda and EventBridge. It is designed to run serverlessly, ensuring that backups are created on a defined schedule without manual intervention.

## Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/aws-lambda-ec2-backup.git
   cd aws-lambda-ec2-backup
   ```

2. **Install dependencies:**

   Ensure you have Python 3.x installed, then run:

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Terraform:**

   Update the `terraform/variables.tf` file with your desired configuration, including AWS region and Lambda function name.

4. **Deploy the infrastructure:**

   Navigate to the `terraform` directory and run:

   ```bash
   terraform init
   terraform apply
   ```

   Confirm the changes when prompted.

## Usage

Once deployed, the Lambda function will automatically create EC2 volume snapshots based on the schedule defined in the EventBridge rule. You can modify the schedule in the Terraform configuration.

## CI/CD

This project includes a CI/CD pipeline configured with GitHub Actions. The pipeline will automatically build, test, and deploy the Lambda function whenever changes are pushed to the repository.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Changelog

See the [CHANGELOG.md](CHANGELOG.md) for a list of changes and updates to the project.