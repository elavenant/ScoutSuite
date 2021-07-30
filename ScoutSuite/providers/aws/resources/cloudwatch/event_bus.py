from ScoutSuite.providers.aws.facade.base import AWSFacade
from ScoutSuite.providers.aws.resources.base import AWSResources
from ScoutSuite.providers.utils import get_non_provider_id


class EventBus(AWSResources):
    def __init__(self, facade: AWSFacade, region: str):
        super().__init__(facade)
        self.region = region

    async def fetch_all(self):
        raw_event_bus = await self.facade.cloudwatch.get_event_bus(self.region)
        self["has_rules"] = await self.facade.cloudwatch.has_event_rules(self.region)
        name, resource = self._parse_event_bus(raw_event_bus)
        self[name] = resource


    def _parse_event_bus(self, raw_event_bus):
        raw_event_bus['arn'] = raw_event_bus.pop('Arn')
        raw_event_bus['name'] = raw_event_bus.pop('Name')

        event_bus_id = get_non_provider_id(raw_event_bus['arn'])

        return event_bus_id, raw_event_bus
