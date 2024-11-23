import os
from aws_cdk import App, Environment
from simple_cdk_app.asg import EcsWithAsgStack

# for development, use account/region from cdk cli
dev_env = Environment(
  # account=os.getenv('CDK_DEFAULT_ACCOUNT'),
  # region=os.getenv('CDK_DEFAULT_REGION'),
  account='792479060307',
  region='us-east-1'
)

app = App()
EcsWithAsgStack(app, "simple-cdk-app-dev", env=dev_env)
# CloudFrontS3(app, "cloudfront-s3-dev", env=dev_env)

app.synth()