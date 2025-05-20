from aws_cdk import (
    # Duration,
    Stack,
    Environment,
    aws_ec2 as ec2,
)
from constructs import Construct
from config.config import Config

from infra.nested_stacks.opensearch_stack import OpensearchStack
class InfraStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, config: Config, env: Environment, **kwargs) -> None:
        super().__init__(scope, construct_id, env=env, **kwargs)
        vpc_config = config.vpc
        vpc = ec2.Vpc.from_lookup(self, id="VPC", vpc_id=vpc_config.id)

        security_group: ec2.SecurityGroup = ec2.SecurityGroup(
            self,
            id="security-group",
            vpc=vpc,
            description=f"Security Group for {config.project_name}",
            allow_all_outbound=True,
        )

        for ingress_rule in [
            "100.0.0.0/8",
            "10.0.0.0/8",
        ]:  # TODO: break this out into config.
            security_group.add_ingress_rule(
                peer=ec2.Peer.ipv4(ingress_rule), connection=ec2.Port.all_traffic()
            )

        opensearch: OpensearchStack = OpensearchStack(
            self, "opensearch-stack", config=config, security_group=security_group, env=env
        )
