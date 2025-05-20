import json
from constructs import Construct
from aws_cdk import (
    RemovalPolicy,
    CfnOutput,
    Environment,
    NestedStack,
    aws_ec2 as ec2,
    aws_opensearchservice as opensearch,
    aws_iam as iam,
    aws_ssm as ssm,
    aws_secretsmanager as secretsmanager,
)

from config.config import Config


class OpensearchStack(NestedStack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        config: Config,
        security_group: ec2.SecurityGroup,
        env: Environment,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        app_name = config.project_name
        opensearch_config = config.opensearch_config

        fine_grained_access = None
        if opensearch_config.fine_grained_access:
            opensearch_secret = secretsmanager.Secret(
                self,
                "OpensearchMasterUserSecret",
                generate_secret_string=secretsmanager.SecretStringGenerator(
                    secret_string_template=json.dumps({"username": "admin"}),
                    generate_string_key="password",
                ),
            )

            fine_grained_access = opensearch.AdvancedSecurityOptions(
                master_user_name=opensearch_secret.secret_value_from_json("username"),
                master_user_password=opensearch_secret.secret_value_from_json(
                    "password"
                ),
            )

        # TODO: Improve this. This is just a test instance
        self.opensearch_domain = opensearch.Domain(
            self,
            "VectorStoreDomain",
            version=opensearch.EngineVersion.OPENSEARCH_2_19,
            domain_name=opensearch_config.domain_name,
            capacity=opensearch.CapacityConfig(
                data_node_instance_type=opensearch_config.instance_type,
                data_nodes=1,
                multi_az_with_standby_enabled=False,  # Must be False for T3 instances
            ),
            ebs=opensearch.EbsOptions(
                enabled=True, volume_size=10, volume_type=ec2.EbsDeviceVolumeType.GP3
            ),
            encryption_at_rest=opensearch.EncryptionAtRestOptions(enabled=True),
            node_to_node_encryption=True,
            enforce_https=True,
            # For testing, allow all access - restrict this for production
            access_policies=[
                iam.PolicyStatement(
                    actions=["es:*"],
                    effect=iam.Effect.ALLOW,
                    principals=[iam.AnyPrincipal()],
                    resources=["*"],
                )
            ],
            removal_policy=RemovalPolicy.DESTROY,
            security_groups=[security_group],
            # Zone awareness must be disabled for single-node T3 deployments
            zone_awareness=opensearch.ZoneAwarenessConfig(enabled=False),
            # Fine-grained access control is optional for testing
            fine_grained_access_control=fine_grained_access,
        )

        # Output the domain endpoint
        CfnOutput(
            self,
            "DomainEndpoint",
            value=self.opensearch_domain.domain_endpoint,
            description="OpenSearch domain endpoint",
        )

        # Output the Kibana endpoint
        CfnOutput(
            self,
            "KibanaEndpoint",
            value=f"{self.opensearch_domain.domain_endpoint}/_dashboards",
            description="OpenSearch dashboard (Kibana) endpoint",
        )

        # Create a new SSM Parameter holding a String
        ssm.StringParameter(
            self,
            id=f"{app_name}-opensearch-ssm",
            description="OpenSearch endpoint for vector store",
            parameter_name=f"/{app_name}/opensearch-endpoint",
            string_value=self.opensearch_domain.domain_endpoint,
        )
