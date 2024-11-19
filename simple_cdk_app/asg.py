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
            instance_type=ec2.InstanceType("t3.micro"),
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

        # Output the cluster name (optional, for debugging)
        print(f"ECS Cluster Name: {cluster.cluster_name}")
