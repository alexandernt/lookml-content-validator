# Where do the files live?
Undder the .github folder in your LookML repository.

# Overview of Content Validator Check

This repository contains a GitHub Action workflow for validating Looker content changes. The workflow consists of a Python script and a YAML file that defines the GitHub Actions workflow.

## Python Script

The Python script `.github/content_validator/content_validator.py` is responsible for validating Looker content changes. Here's a brief overview of its functionality:

- Collects all folder information from Looker.
- Pulls the base URL from the environment variables.
- Collects broken content from Looker.
- Parses broken content and extracts relevant information.
- Compares broken content between production and development branches.
- Outputs any new broken content.

## GitHub Actions Workflow YAML

The GitHub Actions workflow file `.github/workflows/content_validator.yml` defines the workflow for validating Looker content changes. Here's a breakdown of its configuration:

- Triggers the workflow on push and pull requests to the main branch.
- Runs on an Ubuntu latest environment.
- Checks out the code from the repository.
- Sets up Python 3.10.
- Installs dependencies required for the Python script.
- Authenticates with GCP using Workload Identity Pool.
- Fetches secrets from Google Secret Manager.
- Runs the content validation script with necessary environment variables.

### Running Content Validation

The Python script `.github/content_validator/content_validator.py` is executed within the workflow. It validates Looker content changes by comparing broken content between production and development branches. If new broken content is detected, it fails. Have in mind that this validation works only for branches in the Lookml UI.

### Failure Handling

If the content validation script detects new broken content, the workflow fails, indicating that there are issues with Looker content changes. This ensures that any broken content is addressed before merging changes into the main branch.

## Conclusion

The Content Validator Check GitHub Action provides a robust workflow for validating Looker content changes, ensuring the integrity of Looker content in your projects.
