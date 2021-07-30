from asyncio import Lock

from ScoutSuite.core.console import print_exception
from ScoutSuite.providers.aws.facade.basefacade import AWSBaseFacade
from ScoutSuite.providers.aws.facade.utils import AWSFacadeUtils

from ScoutSuite.providers.utils import run_concurrently, get_and_set_concurrently


class Route53Facade(AWSBaseFacade):
    domains = {}
    regional_domains_lock = {}

    async def get_domains(self, region):
        await self._get_domains(region)
        return [domain for domain in self.domains[region]]

    async def _get_domains(self, region):
        async with self.regional_domains_lock.setdefault(region, Lock()):
            if region in self.domains:
                return
            try:
                self.domains[region] = await AWSFacadeUtils.get_all_pages('route53domains', region, self.session,
                                                          'list_domains', 'Domains')
            except Exception as e:
                print_exception(f'Failed to get Route53 domains: {e}')
                self.domains[region] = []
            else:
                await get_and_set_concurrently(
                    [self._get_domain_detail], self.domains[region], region=region)

    async def _get_domain_detail(self, region, domain):
        client = AWSFacadeUtils.get_client('route53domain', self.session, region)
        try:
            index = self.domains[region].index(domain)
            self.domains[region][index]["domain_detail"] = await run_concurrently(
                lambda: client.get_domain_detail(DomainName=domain["DomainName"]))
        except Exception as e:
            print_exception(f'Failed to describe Route53 domain: {e}')

    async def get_hosted_zones(self):
        try:
            return await AWSFacadeUtils.get_all_pages('route53', None, self.session,
                                                      'list_hosted_zones', 'HostedZones')
        except Exception as e:
            print_exception(f'Failed to get Route53 hosted zones: {e}')

    async def get_resource_records(self, hosted_zone_id):
        try:
            return await AWSFacadeUtils.get_all_pages('route53', None, self.session,
                                                      'list_resource_record_sets', 'ResourceRecordSets',
                                                      HostedZoneId=hosted_zone_id)
        except Exception as e:
            print_exception(f'Failed to get Route53 resource records: {e}')

    async def describe_addresses(self, region, addresses):
        res = {}
        client = AWSFacadeUtils.get_client('ec2', self.session, region)
        try:
            metadata = await run_concurrently(
                lambda: client.describe_addresses(
                    PublicIps=addresses)[
                    'Addresses'])
            for address in metadata:
                res[address["PublicIp"]] = address
            for ip in addresses:
                if ip not in res:
                    res[ip] = {}
            return res
        except Exception as e:
            print_exception(f'Failed to describe address: {e}')
