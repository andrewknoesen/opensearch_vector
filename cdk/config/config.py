from enum import Enum
from typing import Dict, List

from dataclasses import dataclass, asdict

from aws_cdk import (
    aws_ec2 as ec2,
)


class AwsAccountNamespace(Enum):
    DEFAULT = "default"


class AwsAccountAlias(Enum):
    DEV = "dev"
    PREPROD = "preprod"
    PROD = "prod"
    DEVOPS = "devops"


@dataclass(frozen=True)
class AwsAccount:
    namespace: AwsAccountNamespace
    number: str
    alias: AwsAccountAlias


class Region(Enum):
    AF_SOUTH_1 = "af-south-1"
    EU_WEST_1 = "eu-west-1"


@dataclass
class OpensearchConfig:
    domain_name: str
    instance_type: str
    fine_grained_access: bool = False


@dataclass
class Tags:
    project_name: str

    def get_tags_dict(self) -> Dict[str, str]:
        return asdict(self)


@dataclass
class SubnetConfig:
    id: str
    az: str


@dataclass
class VpcConfig:
    account: AwsAccount
    region: Region
    id: str
    subnets: List[SubnetConfig]
    
    def get_vpc(self, scope) -> ec2.Vpc:
        return ec2.Vpc.from_lookup(
            scope, id=f'vpc-{self.id}',
            vpc_id=self.id
        )

    def get_subnet_selection(self, scope) -> ec2.SubnetSelection:
        return ec2.SubnetSelection(
            subnets=[
                ec2.Subnet.from_subnet_id(
                    scope, f"Subnet-{subnet.id}", subnet_id=subnet.id
                )
                for subnet in self.subnets
            ]
        )


@dataclass
class Config:
    project_name: str
    vpc: VpcConfig
    tags: Tags
    opensearch_config: OpensearchConfig

    @classmethod
    def new(cls, name: str, vpc: VpcConfig, tags: Tags):
        """
        Factory method that creates a new Config
        """
        return cls(project_name=name, vpc=vpc, tags=tags, opensearch_config=None)

    def register_opensearch(self, opensearch_config: OpensearchConfig):
        self.opensearch_config = opensearch_config
        return self
