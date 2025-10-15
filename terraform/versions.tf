terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.76.1"
    }
  }

  required_version = ">= 0.12"
}

provider "aws" {
  region = var.aws_region
}