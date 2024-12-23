BASIS ```pipx run projen new awscdk-app-py```

Step1. ```cdk deploy EcrStack```

Step2. Deploy docker images to just created repositories. 
Docker deployments are located in the **docker** directory.

```cd docker/fast_api``` - and run docker commands

```cd docker/sftpgo``` - and run docker commands

Step3. replace **domain_name** in app.py with your own

Step4. ```cdk deploy StackWithEcsAndAsg```

> **_NOTE:_**  AmazonECS_FullAccess, AmazonS3FullAccess, AmazonSSMFullAccess, AutoScalingFullAccess, AWSCloudFormationFullAccess, EC2InstanceProfileForImageBuilderECRContainerBuilds roles and such policies should be defined in your IAM user

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "ecr:*",
            "Resource": "*"
        }
    ]
}
```

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "iam:*",
            "Resource": "*"
        }
    ]
}
```
