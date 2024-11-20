from aws_cdk import aws_ec2 as ec2, aws_autoscaling as autoscaling, aws_ecs as ecs, aws_iam as iam
from aws_cdk import App, Stack

class EcsWithAsgStack(Stack):
    def __init__(self, scope, id, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Step 1: Create a VPC
        vpc = ec2.Vpc.from_lookup(self, "defaultVpC",is_default=True, vpc_id="vpc-0d16dafb8b43b505d")

        custom_ami = ec2.MachineImage.generic_linux({
            "eu-central-1": "ami-06e98c6511a4d6aeb",
        })

        instance_role = iam.Role(
            self,
            "EcsInstanceRole",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonEC2ContainerServiceforEC2Role"),
            ],
        )

        # Step 2: Define the User Data for ECS
        user_data = ec2.UserData.for_linux()
        user_data.add_commands("sudo yum update -y")
        user_data.add_commands("echo ECS_CLUSTER=my-ecs-cluster >> /etc/ecs/ecs.config")
        user_data.add_commands("echo ECS_CONTAINER_INSTANCE_PROPAGATE_TAGS_FROM=ec2_instance >> /etc/ecs/ecs.config")

        sg_name = "sg-030f0119fed0f06d5"

        security_group = ec2.SecurityGroup.from_security_group_id(
            self,
            "ExistingSG",
            sg_name
        )

        # Step 3: Define the Launch Template
        launch_template = ec2.LaunchTemplate(
            self,
            "LaunchTemplate",
            machine_image=custom_ami,
            role=instance_role,
            key_name="ubuntu",
            instance_type=ec2.InstanceType("t2.xlarge"),
            security_group=security_group,
            user_data=user_data,  # Pass UserData directly
            associate_public_ip_address = True
        )

        cluster = ecs.Cluster(self, "MyCluster", vpc=vpc, cluster_name="my-ecs-cluster")

        # Step 4: Create the Auto Scaling Group with Launch Template
        asg = autoscaling.AutoScalingGroup(
            self,
            "MyAsg",
            vpc=cluster.vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            launch_template=launch_template,
            min_capacity=1,
            max_capacity=3,
        )

        # Step 5: Create the ECS Cluster


        # Step 6: Attach the ASG to the ECS Cluster using Capacity Provider
        capacity_provider = ecs.AsgCapacityProvider(self, "AsgCapacityProvider", auto_scaling_group=asg)
        cluster.add_asg_capacity_provider(capacity_provider, can_containers_access_instance_role=True)

        task_role = iam.Role.from_role_name(self, "ecsTaskExecutionRole", role_name="ecsTaskExecutionRole")
        #
        fast_api_task_definition = ecs.Ec2TaskDefinition(self,
                                                         "FastApiTaskDefinition",
                                                         execution_role=task_role,
                                                         task_role=task_role,
                                                         network_mode=ecs.NetworkMode.BRIDGE,
                                                         )
        fast_api_container = fast_api_task_definition.add_container(
            "fastapi_app",
            image=ecs.ContainerImage.from_registry("792479060307.dkr.ecr.eu-central-1.amazonaws.com/fastapi_app"),
            memory_limit_mib=3072,
            cpu=1024,
            logging=ecs.LogDrivers.aws_logs(stream_prefix="MyApp")
        )

        fast_api_container.add_port_mappings(
            ecs.PortMapping(container_port=80, host_port=80, protocol=ecs.Protocol.TCP))

        sftp_task_definition = ecs.Ec2TaskDefinition(self,
                                                     "SFTPTaskDefinition",
                                                     execution_role=task_role,
                                                     task_role=task_role,
                                                     network_mode=ecs.NetworkMode.BRIDGE,
                                                     )
        sftp_container = sftp_task_definition.add_container(
            "sftpgo",
            image=ecs.ContainerImage.from_registry("792479060307.dkr.ecr.eu-central-1.amazonaws.com/sftpgo"),
            memory_limit_mib=3072,
            cpu=1024,
            logging=ecs.LogDrivers.aws_logs(stream_prefix="MyApp")
        )

        sftp_container.add_port_mappings(
            ecs.PortMapping(container_port=2022, host_port=2022, protocol=ecs.Protocol.TCP),
            ecs.PortMapping(container_port=8080, host_port=8080, protocol=ecs.Protocol.TCP)
        )

        ecs.Ec2Service(
            self, "FastApiEc2Service",
            cluster=cluster,
            task_definition=fast_api_task_definition,
        )

        ecs.Ec2Service(
            self, "SftpEc2Service",
            cluster=cluster,
            task_definition=sftp_task_definition,
        )

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
        #     targets=[asg]
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
