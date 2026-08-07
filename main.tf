terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

variable "endpoint" {
  type = string
}

provider "aws" {
  access_key = "test"
  secret_key = "test"
  region     = "eu-west-1"

  s3_use_path_style           = true
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true

  endpoints {
    s3 = var.endpoint
  }
}

resource "aws_s3_bucket" "demo" {
  bucket = "terraform-localstack-demo"
}
