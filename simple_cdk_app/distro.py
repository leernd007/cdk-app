from aws_cdk import (
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_certificatemanager as acm,
    aws_s3 as s3,
    aws_elasticloadbalancingv2 as elbv2,
    CfnOutput,
    aws_iam as iam,
    RemovalPolicy,
    aws_s3_deployment as s3_deployment
)
from constructs import Construct
from aws_cdk import App, Stack

class CloudfrontWithALBStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        bucket = s3.Bucket(
            self,
            "MyBucket",
            bucket_name="andriis-static-htmlllll",
            versioned=False,
            auto_delete_objects=True,
            removal_policy=RemovalPolicy.DESTROY,
            website_index_document="index.html"
        )

        s3_deployment.BucketDeployment(
            self,
            "UploadFile",
            sources=[s3_deployment.Source.asset("./web")],  # Local folder or file path
            destination_bucket=bucket
        )

        new_policy = {
            "Version": "2008-10-17",
            "Id": "PolicyForCloudFrontPrivateContent",
            "Statement": [
                {
                    "Sid": "AllowCloudFrontServicePrincipal",
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "cloudfront.amazonaws.com"
                    },
                    "Action": "s3:GetObject",
                    "Resource": "arn:aws:s3:::andriis-static-htmlllll/*"
                }
            ]
        }
        cfn_bucket = s3.CfnBucketPolicy(self, "BucketPolicy",
            bucket="andriis-static-htmlllll",
            policy_document=new_policy
        )


