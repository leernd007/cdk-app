from aws_cdk import (
    aws_ecr as ecr,
    CfnOutput
)
from aws_cdk import App, Stack

class EcrStack(Stack):
    def __init__(self, scope, id, **kwargs):
        super().__init__(scope, id, **kwargs)

        self.fast_api_repo = ecr.Repository(
            self,
            "FastApiRepo",
            repository_name="fastapi_app",
            lifecycle_rules=[
                ecr.LifecycleRule(
                    description="Keep only the last 10 images",
                    max_image_count=10
                )
            ]
        )

        self.sftp_go_repo = ecr.Repository(
            self,
            "SftpGoRepo",
            repository_name="sftpgo",
            lifecycle_rules=[
                ecr.LifecycleRule(
                    description="Keep only the last 10 images",
                    max_image_count=10
                )
            ]
        )
        CfnOutput(self, "FastApiRepoUri", value=self.fast_api_repo.repository_uri, export_name="FastApiRepoUri")
        CfnOutput(self, "SftpGoRepoUri", value=self.sftp_go_repo.repository_uri, export_name="SftpGoRepoUri")
