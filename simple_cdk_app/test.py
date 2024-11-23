certificate = elbv2.ListenerCertificate.from_arn(
    "arn:aws:acm:us-east-1:792479060307:certificate/a909a231-03fc-4a80-976b-1657cd0e3cf0")
domain = "andriispsya.site"
distribution = cloudfront.Distribution(
    self,
    "MyCloudFrontDistribution",
    default_behavior=cloudfront.BehaviorOptions(
        origin=origins.LoadBalancerV2Origin(lb),
        viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
        cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED,
    ),
    domain_names=[domain],  # Replace with your domain name
    certificate=certificate,
)

hosted_zone = route53.HostedZone.from_lookup(
    self,
    "HostedZone",
    domain_name=domain
)

route53.ARecord(
    self,
    "AliasRecord",
    zone=hosted_zone,
    target=route53.RecordTarget.from_alias(targets.CloudFrontTarget(distribution)),
    record_name="",
)

CfnOutput(self, "Api Url", value="https://" + domain)