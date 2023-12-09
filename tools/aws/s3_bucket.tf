provider "aws" {
  region = "ap-northeast-1"
}

# s3 bucket
# https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket
resource "aws_s3_bucket" "terakoya_bucket_public" {
  bucket = "terakoya-bucket-public"
}
resource "aws_s3_bucket" "terakoya_bucket_public_dev" {
  bucket = "terakoya-bucket-public-dev"
}

# Disable public access block for s3 bucket because it is enabled by default.
# https://aws.amazon.com/jp/about-aws/whats-new/2022/12/amazon-s3-automatically-enable-block-public-access-disable-access-control-lists-buckets-april-2023/
resource "aws_s3_bucket_public_access_block" "terakoya_bucket_public_access_block" {
  # 403 error like below occurs when putting policy to s3 bucket without this setting.
  # putting S3 Bucket (terakoya-bucket-public-dev) Policy: operation error S3: PutBucketPolicy, https response error StatusCode: 403, ..., api error AccessDenied: Access Denied
  # https://zenn.dev/hige/articles/01b69444ccaa3d
  bucket = aws_s3_bucket.terakoya_bucket_public.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}
resource "aws_s3_bucket_public_access_block" "terakoya_bucket_public_dev_access_block" {
  bucket = aws_s3_bucket.terakoya_bucket_public_dev.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

# iam policy document for s3 bucket policy
# https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document
data "aws_iam_policy_document" "terakoya_bucket_public_policy_document" {
  statement {
    # Allow all actions for s3 bucket.
    actions = [
      "s3:*"
    ]

    # Allow all resources in the bucket to be accessed.
    resources = [
      "${aws_s3_bucket.terakoya_bucket_public.arn}/*"
    ]

    # Enable all AWS entities (ex: IAM users, IAM roles, AWS accounts, federated users, and assumed roles) to access the bucket.
    principals {
      type = "AWS"
      identifiers = [
        "*"
      ]
    }

    # White list settings
    condition {
      test = "StringLike"
      values = [
        "https://terakoyaweb.com/*"
      ]
      variable = "aws:Referer"
    }
  }
}
data "aws_iam_policy_document" "terakoya_bucket_public_dev_policy_document" {
  statement {
    actions = [
      "s3:*"
    ]

    resources = [
      "${aws_s3_bucket.terakoya_bucket_public_dev.arn}/*"
    ]

    principals {
      type = "AWS"
      identifiers = [
        "*"
      ]
    }

    condition {
      test = "StringLike"
      values = [
        "https://dev.terakoyaweb.com/*", "http://localhost:3000/*", "http://localhost:3001/*", "http://localhost:3002/*"
      ]
      variable = "aws:Referer"
    }
  }
}

# s3 bucket policy
# https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_policy
resource "aws_s3_bucket_policy" "terakoya_bucket_public_policy" {
  bucket = aws_s3_bucket.terakoya_bucket_public.id
  policy = data.aws_iam_policy_document.terakoya_bucket_public_policy_document.json
  # Put the policy after the setting disabling public access block is done.
  depends_on = [ 
    aws_s3_bucket_public_access_block.terakoya_bucket_public_access_block
   ]
}
resource "aws_s3_bucket_policy" "terakoya_bucket_public_dev_policy" {
  bucket = aws_s3_bucket.terakoya_bucket_public_dev.id
  policy = data.aws_iam_policy_document.terakoya_bucket_public_dev_policy_document.json
  depends_on = [ 
    aws_s3_bucket_public_access_block.terakoya_bucket_public_dev_access_block
   ]
}