#!/usr/bin/env python3
import os

from typing import List
import aws_cdk as cdk

from infra.infra_stack import InfraStack

from config.config import (
    Config,
    VpcConfig,
    AwsAccount,
    AwsAccountAlias,
    AwsAccountNamespace,
    SubnetConfig,
    Region,
    Tags,
    OpensearchConfig,
)

PROJECT_NAME = "vector-store-demo"
account = AwsAccount(AwsAccountNamespace.DEFAULT, "308388357296", AwsAccountAlias.DEV)

env = cdk.Environment(account=account.number, region=Region.AF_SOUTH_1.value)

tags: Tags = Tags(project_name=PROJECT_NAME)

subnets: List[SubnetConfig]= [
    SubnetConfig(id="subnet-0761dd00295d799f8", az="afs1-az1"),
    SubnetConfig(id="subnet-0c707f058b5af7e8e", az="afs1-az2"),
    SubnetConfig(id="subnet-04993ba77f8bc5bc9", az="afs1-az3")
    ]

vpc: VpcConfig = VpcConfig(
    account=account, region=Region.AF_SOUTH_1, id="vpc-00a0b4c73f0b4d095", subnets=subnets
)
config: Config = (
    Config.new(PROJECT_NAME, vpc, tags)
    .register_opensearch(OpensearchConfig(PROJECT_NAME, "t3.small.search", fine_grained_access=True)))

app = cdk.App()
InfraStack(
    app,
    "InfraStack",
    config=config,
    env=env,
)

app.synth()
