---
title: "AWS"
description: "Generate presigned S3 URLs for secure, time-limited object access"
---

# AWS

> Generate presigned S3 URLs for secure, time-limited object access

The AWS integration lets your workflows interact with Amazon Web Services using IAM user credentials. The current action is **S3 Get Presigned URL**, which generates a time-limited download link for any object in an S3 bucket without requiring the caller to have AWS credentials.

## Authentication

AWS uses IAM user access keys.

<Steps>
  <Step title="Create an IAM user">
    In the AWS console, create a dedicated IAM user with `s3:GetObject` permission scoped to the relevant buckets (or a specific key prefix).
  </Step>

  <Step title="Generate access keys">
    Under the IAM user's **Security credentials** tab, create an access key and copy the Access Key ID and Secret Access Key.
  </Step>

  <Step title="Add a credential in HappyRobot">
    Go to **Settings > Integrations**, enable **AWS**, click **Add Credential**, and fill in:

    * **Access Key ID** — the IAM user's access key ID
    * **Secret Access Key** — the IAM user's secret access key
    * **Region** — the AWS region your bucket lives in (for example, `us-east-1`)
  </Step>

  <Step title="Verify the credential">
    Save the credential and verify it appears as **Active**.
  </Step>
</Steps>

<Info>
  Use a dedicated IAM user with the minimum permissions your workflow needs. For **S3 Get Presigned URL**, the user requires `s3:GetObject` on the target bucket (or a specific key prefix).
</Info>

## Available actions

### S3 Get Presigned URL

Generates a presigned download URL for an S3 object. The URL grants temporary, unauthenticated read access to the object — useful for sharing files with callers, email recipients, or external services without exposing your AWS credentials.

**Configuration:**

| Field                    | Required | Description                                                                     |
| ------------------------ | -------- | ------------------------------------------------------------------------------- |
| **AWS Credential**       | Yes      | The IAM credential to authenticate with                                         |
| **Bucket**               | Yes      | The S3 bucket name (supports variables)                                         |
| **Key**                  | Yes      | The object key (path) within the bucket (supports variables)                    |
| **Expiration (seconds)** | No       | How long the URL is valid. Default: `3600` (1 hour). Maximum: `604800` (7 days) |

All fields support [variable templating](../../02-Workflows/07-Variables.md) — use `@` to reference values from upstream nodes.

**Output fields:**

| Field           | Type   | Description                             |
| --------------- | ------ | --------------------------------------- |
| `presigned_url` | string | The temporary download URL              |
| `expires_at`    | string | ISO 8601 timestamp when the URL expires |
| `bucket`        | string | The bucket name used                    |
| `key`           | string | The object key used                     |

## Example use case

After a voice agent collects a load confirmation from a carrier, a webhook trigger provides the S3 key of the confirmation document. The workflow uses **S3 Get Presigned URL** to generate a download link, then sends it to the carrier via SMS so they can retrieve the document immediately.

## Related

<CardGroup cols={2}>
  <Card title="Webhook node" icon="webhook" href="../../03-Core-Nodes/06-Webhook.md">
    Trigger workflows or call external APIs from within a run.
  </Card>

  <Card title="File Operations" icon="file" href="../../03-Core-Nodes/08-File-Operations.md">
    Read and process files in your workflows.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/integrations/data/aws
