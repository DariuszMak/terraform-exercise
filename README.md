# Python project

### Project structure diagrams

##### Modular perspective

<p align="center">
  <img src="images/structure_module.svg" alt="Modular perspective" width="600">
</p>

### Structurizr diagrams

<table align="center">
    <tr>
        <td align="center">
            <img src="images/Structurizr/SystemLandscape-dark.svg" width="1200px">
        </td>
    </tr>
    <tr>
    <td align="center">
        <img src="images/Structurizr/Components-dark.svg" width="600px">
    </td>
    <td></td>
    <td align="center">
        <img src="images/Structurizr/DevelopmentWorkflow-dark.svg" width="600px">
    </td>
</table>

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

This starts a LocalStack container, waits for the S3 service to become available, then runs `terraform init`/`terraform apply` against `main.tf` to create the `terraform-localstack-demo` bucket, uploads a test file, and opens it in the browser.
