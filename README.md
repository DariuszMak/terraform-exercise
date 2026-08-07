# Python project

### Project structure diagrams

##### Modular perspective

<p align="center">
  <img src="images/structure_module.svg" alt="Modular perspective" width="600">
</p>

##### Library dependencies perspective

<p align="center">
  <img src="images/structure_module_clustered.svg" alt="Library dependencies perspective" width="600">
</p>

## Requirements

- [UV](https://github.com/astral-sh/uv) package manager
- [Task](https://taskfile.dev/docs/installation) runner
- [Docker](https://www.docker.com/) for LocalStack
- [Terraform](https://developer.hashicorp.com/terraform/install)
- [AWS CLI](https://aws.amazon.com/cli/)

### Fast Windows dev

```commandline
task full-dev-native ; 
```

### Generate diagrams

```commandline
task generate-diagrams ; 
```

### LocalStack + Terraform S3 demo

```commandline
task localstack-terraform ; 
```

or, including a full cleanup first:

```commandline
task full-dev-localstack ; 
```

This starts a LocalStack container, waits for the S3 service to become available, then runs `terraform init`/`terraform apply` against `main.tf` to create the `terraform-localstack-demo` bucket, uploads a test file, and opens it in the browser.
