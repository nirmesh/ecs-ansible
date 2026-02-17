#!/usr/bin/env python3
"""Create a WORM (Object Lock) bucket on S3-compatible storage, including Pure Storage FlashBlade."""

from __future__ import annotations

import argparse
import sys

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create an S3 Object Lock (WORM) bucket and apply a default retention policy."
        )
    )
    parser.add_argument("--endpoint-url", required=True, help="S3 endpoint URL")
    parser.add_argument("--access-key", required=True, help="S3 access key")
    parser.add_argument("--secret-key", required=True, help="S3 secret key")
    parser.add_argument("--bucket", required=True, help="Bucket name to create")
    parser.add_argument(
        "--region",
        default="us-east-1",
        help="S3 region name (default: us-east-1)",
    )
    parser.add_argument(
        "--retention-days",
        type=int,
        default=30,
        help="Default object retention in days (default: 30)",
    )
    parser.add_argument(
        "--retention-mode",
        choices=["COMPLIANCE", "GOVERNANCE"],
        default="COMPLIANCE",
        help="Object Lock mode (default: COMPLIANCE)",
    )
    parser.add_argument(
        "--insecure",
        action="store_true",
        help="Disable TLS certificate verification",
    )
    return parser.parse_args()


def create_worm_bucket(args: argparse.Namespace) -> None:
    client = boto3.client(
        "s3",
        endpoint_url=args.endpoint_url,
        aws_access_key_id=args.access_key,
        aws_secret_access_key=args.secret_key,
        region_name=args.region,
        verify=not args.insecure,
        config=Config(s3={"addressing_style": "path"}),
    )

    # Object Lock must be enabled at bucket creation time.
    create_params = {
        "Bucket": args.bucket,
        "ObjectLockEnabledForBucket": True,
    }
    if args.region != "us-east-1":
        create_params["CreateBucketConfiguration"] = {
            "LocationConstraint": args.region
        }

    client.create_bucket(**create_params)

    # Object Lock requires versioning to be enabled.
    client.put_bucket_versioning(
        Bucket=args.bucket,
        VersioningConfiguration={"Status": "Enabled"},
    )

    client.put_object_lock_configuration(
        Bucket=args.bucket,
        ObjectLockConfiguration={
            "ObjectLockEnabled": "Enabled",
            "Rule": {
                "DefaultRetention": {
                    "Mode": args.retention_mode,
                    "Days": args.retention_days,
                }
            },
        },
    )


def main() -> int:
    args = parse_args()

    try:
        create_worm_bucket(args)
    except ClientError as exc:
        print(f"Failed to create WORM bucket: {exc}", file=sys.stderr)
        return 1

    print(
        f"Created bucket '{args.bucket}' with Object Lock mode={args.retention_mode} "
        f"and retention_days={args.retention_days}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
