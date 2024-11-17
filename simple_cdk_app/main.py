import os
from constructs import Construct

from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_iam as iam,
    aws_autoscaling as autoscaling,
    Fn
)

class MyStack(Stack):
  def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
    super().__init__(scope, construct_id, **kwargs)

    vpc = ec2.Vpc.from_lookup(self, "Vpc",is_default=True)

    sg_name = "sg-030f0119fed0f06d5"

    security_group = ec2.SecurityGroup.from_security_group_id(
      self,
      "ExistingSG",
      sg_name
    )

    cluster = ecs.Cluster(self, "ECSCluster", vpc=vpc)

    user_data = ec2.UserData.for_linux()
    user_data.add_commands(
      "echo ECS_CLUSTER=my-cluster-name >> /etc/ecs/ecs.config",
      "yum install -y aws-cli"
    )

    key_pair = ec2.KeyPair.from_key_pair_attributes(self, "KeyPair",
        key_pair_name="ubuntu"
    )
    ecs_instance_role = iam.Role(self, "EcsInstanceRole",
                                 assumed_by=iam.ServicePrincipal("ec2.amazonaws.com")
                                 )

    ecs_instance_role.add_managed_policy(
        iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonEC2ContainerServiceforEC2Role")
    )
    launch_template = ec2.LaunchTemplate(self, "LaunchTemplate",
       machine_image=ec2.MachineImage.latest_amazon_linux2023(),
       security_group=security_group,
       instance_type = ec2.InstanceType.of(ec2.InstanceClass.T2, ec2.InstanceSize.XLARGE),
       key_pair = key_pair,
       launch_template_name = "ECSLaunchTemplate",
       user_data=user_data,
       role=ecs_instance_role
    )

    asg = autoscaling.AutoScalingGroup(
      self,
      "EcsAsg",
      vpc=vpc,
      min_capacity=1,
      max_capacity=2,
      desired_capacity=1,
      launch_template=launch_template,
      vpc_subnets=ec2.SubnetSelection(
        subnet_type=ec2.SubnetType.PUBLIC  # Default Subnets
      )
    )

    asg.add_user_data(
      "echo 'Enable auto-assign public IP' >> /var/log/user-data.log"
    )

    cluster.add_asg_capacity_provider(
      ecs.AsgCapacityProvider(self, "AsgCapacityProvider", auto_scaling_group=asg)
    )
