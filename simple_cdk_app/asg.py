from aws_cdk import (
    aws_ec2 as ec2,
    aws_autoscaling as autoscaling,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_ecs as ecs,
    aws_iam as iam,
    aws_route53 as route53,
    aws_route53_targets as targets,
    aws_elasticloadbalancingv2 as elbv2,
    CfnOutput,
    aws_certificatemanager as acm,
    aws_s3 as s3,
    aws_route53_targets as route53_targets,
    RemovalPolicy,
    aws_s3_deployment as s3_deployment,
)
from aws_cdk import App, Stack

class EcsWithAsgStack(Stack):
    def __init__(self, scope, id, **kwargs):
        super().__init__(scope, id, **kwargs)

        vpc = ec2.Vpc(
            self,
            "DefaultVpc",
            max_azs=3,
            nat_gateways=1,
        )

        instance_role = iam.Role(
            self,
            "EcsInstanceRole",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonEC2ContainerServiceforEC2Role"),
            ],
        )

        user_data = ec2.UserData.for_linux()

        def define_sg_grop():
            security_group = ec2.SecurityGroup(
                self,
                "CustomSecurityGroup",
                vpc=vpc,
                security_group_name="MyCustomSecurityGroup",
                allow_all_outbound=True,  # Allow all outbound traffic
                description="Security group with specific inbound rules",
            )

            # Add inbound rules
            security_group.add_ingress_rule(
                peer=ec2.Peer.any_ipv4(),  # Allow from any IPv4
                connection=ec2.Port.tcp(22),  # SSH
                description="Allow SSH traffic on port 22",
            )

            security_group.add_ingress_rule(
                peer=ec2.Peer.any_ipv4(),
                connection=ec2.Port.tcp(443),  # HTTPS
                description="Allow HTTPS traffic on port 443",
            )

            security_group.add_ingress_rule(
                peer=ec2.Peer.any_ipv4(),
                connection=ec2.Port.tcp(8080),  # Custom TCP port 8080
                description="Allow traffic on port 8080",
            )

            security_group.add_ingress_rule(
                peer=ec2.Peer.any_ipv4(),
                connection=ec2.Port.icmp_ping(),  # ICMP for ping
                description="Allow all ICMP traffic (e.g., ping)",
            )

            security_group.add_ingress_rule(
                peer=ec2.Peer.any_ipv4(),
                connection=ec2.Port.tcp(2022),  # Custom TCP port 2022
                description="Allow traffic on port 2022",
            )

            security_group.add_ingress_rule(
                peer=ec2.Peer.any_ipv4(),
                connection=ec2.Port.tcp(80),  # HTTP
                description="Allow HTTP traffic on port 80",
            )

            return security_group

        security_group = define_sg_grop()

        #
        custom_ami = ec2.MachineImage.generic_linux({
            "us-east-1": "ami-02b21406128600b18",
        })

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
            image=ecs.ContainerImage.from_registry("792479060307.dkr.ecr.us-east-1.amazonaws.com/fastapi_app"),
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
            image=ecs.ContainerImage.from_registry("792479060307.dkr.ecr.us-east-1.amazonaws.com/sftpgo"),
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

        lb = elbv2.ApplicationLoadBalancer(self, "LB", vpc=vpc, internet_facing=True, load_balancer_name="AndriisLB")
        hosted_zone = route53.HostedZone.from_lookup(
            self,
            "HostedZone",
            domain_name="andriispsya.site"
        )
        certificate = acm.Certificate(
            self,
            "SiteCertificate",
            domain_name="andriispsya.site",  # Replace with your domain
            validation=acm.CertificateValidation.from_dns(hosted_zone),  # Use DNS validation
        )


        listener = lb.add_listener(
            "Listener",
            port=80,
            # certificates=[certificate]
        )
        listener.add_targets(
            "FastApiTargetGroup",
            port=80,
            health_check=elbv2.HealthCheck(
                path="/",
                healthy_http_codes="200",
                port="80"
            ),
            target_group_name="FastApiTargetGroup",
            targets=[asg]
        )
        listener.add_targets(
            "SftpTargetGroup",
            port=8080,
            target_group_name="SftpTargetGroup",
            health_check=elbv2.HealthCheck(
                path="/web/admin/setup",  #
                healthy_http_codes="200",
                port="8080"
            ),
            conditions=[
                elbv2.ListenerCondition.path_patterns(["/sftp/*"])
            ],
            priority=1,
            targets=[asg]
        )
        CfnOutput(self, "LoadBalancerDNS", value=lb.load_balancer_dns_name)
        sftp_bucket_name = 'andriis-sftp-files'
        sftp_bucket = s3.Bucket(
            self,
            "MySftpBucket",
            bucket_name=sftp_bucket_name,
            versioned=False,
            auto_delete_objects=True,
            removal_policy=RemovalPolicy.DESTROY
        )

        # just to deploy test files
        s3_deployment.BucketDeployment(
            self,
            "UploadSftpFile",
            sources=[s3_deployment.Source.asset("./web")],  # Local folder or file path
            destination_bucket=sftp_bucket
        )
        # {
        #     "Version": "2008-10-17",
        #     "Id": "PolicyForCloudFrontPrivateContent",
        #     "Statement": [
        #         {
        #             "Sid": "AllowCloudFrontServicePrincipal",
        #             "Effect": "Allow",
        #             "Principal": {
        #                 "Service": "cloudfront.amazonaws.com"
        #             },
        #             "Action": "s3:GetObject",
        #             "Resource": "arn:aws:s3:::andriis-sftp-files/*",
        #             "Condition": {
        #                 "StringEquals": {
        #                     "AWS:SourceArn": "arn:aws:cloudfront::792479060307:distribution/E2RAPD4YNPLOXR"
        #                 }
        #             }
        #         }
        #     ]
        # }
        sftp_bucket_policy = {
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
                    "Resource": "arn:aws:s3:::" + sftp_bucket_name + "/*"
                }
            ]
        }

        s3.CfnBucketPolicy(self, "SftpBucketPolicy",
            bucket=sftp_bucket_name,
            policy_document=sftp_bucket_policy
        )

        bucket_name = "andriis-static-html"
        bucket = s3.Bucket(
            self,
            "MyBucket",
            bucket_name=bucket_name,
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
                    "Resource": "arn:aws:s3:::" + bucket_name + "/*"
                }
            ]
        }
        cfn_bucket = s3.CfnBucketPolicy(self, "BucketPolicy",
            bucket=bucket_name,
            policy_document=new_policy
        )

        oac = cloudfront.S3OriginAccessControl(self, "MyOAC",
                                               signing=cloudfront.Signing.SIGV4_NO_OVERRIDE
                                               )
        s3_origin = origins.S3BucketOrigin.with_origin_access_control(bucket,
                                                                      origin_access_control=oac
                                                                      )
        distribution = cloudfront.Distribution(
            self,
            "MyCloudFrontDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=s3_origin,
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS
            ),
            additional_behaviors={
                "/api": cloudfront.BehaviorOptions(
                    origin=origins.LoadBalancerV2Origin(lb, protocol_policy=cloudfront.OriginProtocolPolicy.HTTP_ONLY),
                    cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
                    origin_request_policy=cloudfront.OriginRequestPolicy.ALL_VIEWER,
                    viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS
                ),
                "/sftp/*": cloudfront.BehaviorOptions(
                    origin=origins.LoadBalancerV2Origin(lb, protocol_policy=cloudfront.OriginProtocolPolicy.HTTP_ONLY),
                    cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
                    origin_request_policy=cloudfront.OriginRequestPolicy.ALL_VIEWER,
                    viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS
                )
            },
            domain_names=["andriispsya.site"],
            default_root_object="index.html",
            certificate=certificate
        )

        route53.ARecord(
            self,
            "AliasRecord",
            zone=hosted_zone,
            target=route53.RecordTarget.from_alias(route53_targets.CloudFrontTarget(distribution)),
            record_name="",
        )

        CfnOutput(
            self,
            "CloudFrontDomainName",
            value=distribution.distribution_domain_name,
            description="The domain name of the CloudFront distribution",
        )