import os
from aws_cdk import App, Environment
from simple_cdk_app.asg import StackWithEcsAndAsg
from simple_cdk_app.ecr import EcrStack

# for development, use account/region from cdk cli
dev_env = Environment(
  account=os.getenv('CDK_DEFAULT_ACCOUNT'),
  region=os.getenv('CDK_DEFAULT_REGION')
)

app = App()
EcrStack(app, "EcrStack", env=dev_env)
StackWithEcsAndAsg(app, "StackWithEcsAndAsg", env=dev_env, domain_name="andriispsya.site")

app.synth()