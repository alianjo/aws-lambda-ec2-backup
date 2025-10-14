# CHANGELOG

## [1.0.0] - 2023-10-01
### Added
- Initial release of the AWS Lambda EC2 backup system.
- Implemented main Lambda function handler in `src/handler.py`.
- Created utility functions in `src/utils.py`.
- Defined infrastructure resources in `terraform/main.tf`.
- Added input variables in `terraform/variables.tf`.
- Specified outputs in `terraform/outputs.tf`.
- Set required provider versions in `terraform/versions.tf`.
- Configured CI/CD pipeline in `.github/workflows/ci-cd.yml`.
- Listed dependencies in `requirements.txt`.
- Created README.md for project documentation.