import os
from constructs import Construct

from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_iam as iam,
    aws_autoscaling as autoscaling,
    Fn,
    CfnOutput,
    aws_certificatemanager as acm,
    aws_elasticloadbalancingv2 as elbv2
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

    user_data = ec2.UserData.for_linux()
    user_data.add_commands(
      "yum install -y aws-cli",
      "echo ECS_CLUSTER=ECSCluster >> /etc/ecs/ecs.config",
      "start ecs"
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

    user_data_v1 = """
#!/bin/bash
"yum install -y aws-cli",
"echo ECS_CLUSTER=ECSCluster >> /etc/ecs/ecs.config",
"start ecs"
    """
    launch_template = ec2.CfnLaunchTemplate(self, "LaunchTemplate",
       launch_template_data=ec2.CfnLaunchTemplate.LaunchTemplateDataProperty(
        instance_type="t2.xlarge",
        user_data=user_data_v1,
        key_name="ubuntu",
        role=instance_role,
        security_group_ids=[security_group.security_group_id],
        # security_groups=["sg-030f0119fed0f06d5"],
        # iam_instance_profile=instance_profile,
        image_id=ec2.AmazonLinuxImage().get_image(self).image_id
       )
    )
    referenced_launch_template = ec2.LaunchTemplate.from_launch_template_attributes(
        self, "ReferencedLaunchTemplate",
        launch_template_id=launch_template.ref,
        version_number="1"
    )
    asg = autoscaling.AutoScalingGroup(
      self,
      "EcsAsg",
      vpc=vpc,
      min_capacity=1,
      max_capacity=2,
      desired_capacity=1,
      # user_data=user_data,
      # security_group=security_group,
      launch_template=referenced_launch_template,
      vpc_subnets=ec2.SubnetSelection(
        subnet_type=ec2.SubnetType.PUBLIC  # Default Subnets
      ),
    )

    cluster = ecs.Cluster(self, "ECSCluster", vpc=vpc)
    cluster.add_capacity("DefaultAutoScalingGroupCapacity",
                         instance_type=ec2.InstanceType("t2.xlarge"),
                         desired_capacity=1,
                         associate_public_ip_address=True
                         )
    # capacity_provider = ecs.AsgCapacityProvider(self, "AsgCapacityProvider",auto_scaling_group=asg, machine_image_type=ecs.MachineImageType.AMAZON_LINUX_2)
    # cluster.add_asg_capacity_provider(capacity_provider)
    #
    # task_role = iam.Role.from_role_name(self, "ecsTaskExecutionRole", role_name="ecsTaskExecutionRole")
    # #
    # fast_api_task_definition = ecs.Ec2TaskDefinition(self,
    #     "FastApiTaskDefinition",
    #     execution_role=task_role,
    #     task_role=task_role,
    #     network_mode=ecs.NetworkMode.BRIDGE,
    # )
    # fast_api_container = fast_api_task_definition.add_container(
    #     "fastapi_app",
    #     image=ecs.ContainerImage.from_registry("792479060307.dkr.ecr.eu-central-1.amazonaws.com/fastapi_app"),
    #     memory_limit_mib=3072,
    #     cpu=1024,
    #     logging=ecs.LogDrivers.aws_logs(stream_prefix="MyApp")
    # )
    #
    # fast_api_container.add_port_mappings( ecs.PortMapping(container_port=80, host_port=80, protocol=ecs.Protocol.TCP))
    #
    #
    # sftp_task_definition = ecs.Ec2TaskDefinition(self,
    #     "SFTPTaskDefinition",
    #     execution_role=task_role,
    #     task_role=task_role,
    #     network_mode=ecs.NetworkMode.BRIDGE,
    # )
    # sftp_container = sftp_task_definition.add_container(
    #     "sftpgo",
    #     image=ecs.ContainerImage.from_registry("792479060307.dkr.ecr.eu-central-1.amazonaws.com/sftpgo"),
    #     memory_limit_mib=3072,
    #     cpu=1024,
    #     logging=ecs.LogDrivers.aws_logs(stream_prefix="MyApp")
    # )
    #
    # sftp_container.add_port_mappings(
    #     ecs.PortMapping(container_port=2022, host_port=2022, protocol=ecs.Protocol.TCP),
    #     ecs.PortMapping(container_port=8080, host_port=8080, protocol=ecs.Protocol.TCP)
    # )
    #
    # ecs.Ec2Service(
    #     self, "FastApiEc2Service",
    #     cluster=cluster,
    #     task_definition=fast_api_task_definition,
    # )
    #
    # ecs.Ec2Service(
    #     self, "SftpEc2Service",
    #     cluster=cluster,
    #     task_definition=sftp_task_definition,
    # )

    # lb = elbv2.ApplicationLoadBalancer(self, "LB", vpc=vpc, internet_facing=True, load_balancer_name="AndriisLB")
    #
    # certificate_arn = "arn:aws:acm:eu-central-1:792479060307:certificate/ec3fd1a9-b3df-4783-baed-2c1af2061a1e"
    #
    # listener = lb.add_listener(
    #     "Listener",
    #     port=443,
    #     certificates=[elbv2.ListenerCertificate.from_arn(certificate_arn)]
    # )
    # listener.add_targets(
    #     "FastApiTargetGroup",
    #     port=80,
    #     health_check=elbv2.HealthCheck(
    #         path="/",
    #         healthy_http_codes="200",
    #         port="80"
    #     ),
    #     target_group_name="FastApiTargetGroup",
    #     targets = [asg]
    # )
    # listener.add_targets(
    #     "SftpTargetGroup",
    #     port=8080,
    #     target_group_name="SftpTargetGroup",
    #     health_check=elbv2.HealthCheck(
    #         path="/web/admin/setup",  #
    #         healthy_http_codes="200",
    #         port="8080"
    #     ),
    #     conditions=[
    #         elbv2.ListenerCondition.path_patterns(["/sftp/*"])
    #     ],
    #     priority=1,
    #     targets=[asg]
    # )
    # CfnOutput(self, "LoadBalancerDNS", value=lb.load_balancer_dns_name)