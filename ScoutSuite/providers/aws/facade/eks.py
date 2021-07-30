from asyncio import Lock

from ScoutSuite.core.console import print_exception
from ScoutSuite.providers.aws.facade.basefacade import AWSBaseFacade
from ScoutSuite.providers.aws.facade.utils import AWSFacadeUtils
from ScoutSuite.providers.utils import run_concurrently, get_and_set_concurrently
from ScoutSuite.utils import manage_dictionary


class EKSFacade(AWSBaseFacade):
    regional_clusters_eks_locks = {}
    regional_subnets_eks_locks = {}
    clusters_eks = {}
    subnets_eks = {}

    async def get_clusters(self, region):
        await self.eks_clusters(region)
        return [cluster for cluster in self.clusters_eks[region]]

    async def eks_clusters(self, region):
        async with self.regional_clusters_eks_locks.setdefault(region, Lock()):
            if region in self.clusters_eks:
                return

            self.clusters_eks[region] = await AWSFacadeUtils.get_all_pages(
                'eks', region, self.session, 'list_clusters', 'clusters')

            await get_and_set_concurrently(
                [self._describe_cluster], self.clusters_eks[region], region=region)
            await get_and_set_concurrently(
                [self.get_security_groups], self.clusters_eks[region], region=region)

    async def _describe_cluster(self, cluster: str, region: str):
        client = AWSFacadeUtils.get_client('eks', self.session, region)
        try:
            self.clusters_eks[region].remove(cluster)
            self.clusters_eks[region].append(await run_concurrently(
                lambda: client.describe_cluster(name=cluster)['cluster']))
        except Exception as e:
            print_exception(f'Failed to describe EKS cluster: {e}')

    async def get_security_groups(self, cluster, region):
        filters = [{'Name': 'group-id', 'Values': [cluster["resourcesVpcConfig"]["clusterSecurityGroupId"]]}]
        client = AWSFacadeUtils.get_client('ec2', self.session, region)
        try:
            raw_security_groups=  await AWSFacadeUtils.get_all_pages(
            'ec2', region, self.session, 'describe_security_groups', 'SecurityGroups', Filters=filters)
            index = self.clusters_eks[region].index(cluster)
            for raw_security_groups in raw_security_groups:
                name, self.clusters_eks[region][index]["securityGroup"] = self._parse_security_group(raw_security_groups)
        except Exception as e:
            print_exception(f'Failed to describe EKS security groups: {e}')

    def _parse_security_group(self, raw_security_group):
        security_group = {}
        security_group['name'] = raw_security_group['GroupName']
        security_group['id'] = raw_security_group['GroupId']
        security_group['description'] = raw_security_group['Description']
        security_group['owner_id'] = raw_security_group['OwnerId']

        if 'Tags' in raw_security_group:
            security_group['tags'] = {x['Key']: x['Value'] for x in raw_security_group['Tags']}

        security_group['rules'] = {'ingress': {}, 'egress': {}}
        ingress_protocols, ingress_rules_count = self._parse_security_group_rules(
            raw_security_group['IpPermissions'])
        security_group['rules']['ingress']['protocols'] = ingress_protocols
        security_group['rules']['ingress']['count'] = ingress_rules_count

        egress_protocols, egress_rules_count = self._parse_security_group_rules(
            raw_security_group['IpPermissionsEgress'])
        security_group['rules']['egress']['protocols'] = egress_protocols
        security_group['rules']['egress']['count'] = egress_rules_count

        security_group['is_default_configuration'] = \
            self._has_default_egress_rule(raw_security_group['IpPermissionsEgress']) and \
            self._has_default_ingress_rule(raw_security_group['IpPermissions'], raw_security_group['GroupId'])

        return security_group['id'], security_group

    def _has_default_egress_rule(self, rule_list):
        for rule in rule_list:
            if rule['IpProtocol'] == '-1':
                for ip_range in rule['IpRanges']:
                    if ip_range['CidrIp'] == '0.0.0.0/0':
                        return True
        return False

    def _has_default_ingress_rule(self, rule_list, group_id):
        for rule in rule_list:
            if rule['IpProtocol'] == '-1':
                for source_group in rule['UserIdGroupPairs']:
                    if source_group['GroupId'] == group_id:
                        return True
        return False

    def _parse_security_group_rules(self, rules):
        protocols = {}
        rules_count = 0
        for rule in rules:
            ip_protocol = rule['IpProtocol'].upper()
            if ip_protocol == '-1':
                ip_protocol = 'ALL'
            protocols = manage_dictionary(protocols, ip_protocol, {})
            protocols[ip_protocol] = manage_dictionary(
                protocols[ip_protocol], 'ports', {})

            # Save the port (single port or range)
            port_value = '1-65535'
            if 'FromPort' in rule and 'ToPort' in rule:
                if ip_protocol == 'ICMP':
                    # FromPort with ICMP is the type of message
                    port_value = self.icmp_message_types_dict[str(
                        rule['FromPort'])]
                elif rule['FromPort'] == rule['ToPort']:
                    port_value = str(rule['FromPort'])
                else:
                    port_value = '{}-{}'.format(rule['FromPort'], rule['ToPort'])
            manage_dictionary(protocols[ip_protocol]['ports'], port_value, {})

            # Save grants, values are either a CIDR or an EC2 security group
            for grant in rule['UserIdGroupPairs']:
                manage_dictionary(
                    protocols[ip_protocol]['ports'][port_value], 'security_groups', [])
                protocols[ip_protocol]['ports'][port_value]['security_groups'].append(
                    grant)
                rules_count = rules_count + 1
            for grant in rule['IpRanges']:
                manage_dictionary(
                    protocols[ip_protocol]['ports'][port_value], 'cidrs', [])
                protocols[ip_protocol]['ports'][port_value]['cidrs'].append(
                    {'CIDR': grant['CidrIp']})
                rules_count = rules_count + 1

            # IPv6
            for grant in rule['Ipv6Ranges']:
                manage_dictionary(
                    protocols[ip_protocol]['ports'][port_value], 'cidrs', [])
                protocols[ip_protocol]['ports'][port_value]['cidrs'].append(
                    {'CIDR': grant['CidrIpv6']})
                rules_count = rules_count + 1

        return protocols, rules_count