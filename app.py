import os
from aws_cdk import App, Environment
from simple_cdk_app.main import MyStack

# for development, use account/region from cdk cli
dev_env = Environment(
  # account=os.getenv('CDK_DEFAULT_ACCOUNT'),
  # region=os.getenv('CDK_DEFAULT_REGION'),
  account='792479060307',
  region='eu-central-1'
)

app = App()
MyStack(app, "simple-cdk-app-dev", env=dev_env)
# MyStack(app, "simple_cdk_app-prod", env=prod_env)

app.synth()