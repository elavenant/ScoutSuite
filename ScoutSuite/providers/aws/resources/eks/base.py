from ScoutSuite.providers.aws.facade.base import AWSFacade
from ScoutSuite.providers.aws.resources.regions import Regions

from .clusters import Clusters


class EKS(Regions):
    _children = [
        (Clusters, 'clusters')
    ]

    def __init__(self, facade: AWSFacade):
        super().__init__('eks', facade)

    async def fetch_all(self, regions=None, excluded_regions=None, partition_name='aws', **kwargs):
        await super().fetch_all(regions, excluded_regions, partition_name)

        for region in self['regions']:
            self['regions'][region]['clusters_count'] = \
                len(self['regions'][region]['clusters'])

        self['clusters_count'] = sum([region['clusters_count'] for region in self['regions'].values()])
