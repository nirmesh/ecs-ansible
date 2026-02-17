# ecs-ansible

## Create a WORM bucket on Pure Storage (S3-compatible)

Use `create_worm_bucket.py` to create an S3 bucket with Object Lock enabled (WORM behavior) and apply a default retention rule.

### Requirements

- Python 3.8+
- `boto3` (`pip install boto3`)

### Example

```bash
python3 create_worm_bucket.py \
  --endpoint-url https://<flashblade-or-s3-endpoint> \
  --access-key <ACCESS_KEY> \
  --secret-key <SECRET_KEY> \
  --bucket finance-records-worm \
  --region us-east-1 \
  --retention-mode COMPLIANCE \
  --retention-days 365
```

### Notes

- Object Lock must be enabled when the bucket is created.
- Bucket versioning is enabled by the script because Object Lock requires versioning.
- `--retention-mode` can be `COMPLIANCE` or `GOVERNANCE`.
- Use `--insecure` only for lab/test environments with self-signed certificates.
