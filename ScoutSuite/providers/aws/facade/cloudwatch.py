from ScoutSuite.core.console import print_exception
from ScoutSuite.providers.aws.facade.basefacade import AWSBaseFacade
from ScoutSuite.providers.aws.facade.utils import AWSFacadeUtils
from ScoutSuite.providers.utils import run_concurrently, get_and_set_concurrently


class CloudWatch(AWSBaseFacade):

    async def get_alarms(self, region):
        try:
            return await AWSFacadeUtils.get_all_pages('cloudwatch', region, self.session, 'describe_alarms',
                                                      'MetricAlarms')
        except Exception as e:
            print_exception(f'Failed to get CloudWatch alarms: {e}')
            return []

    async def get_metric_filters(self, region):
        try:
            return await AWSFacadeUtils.get_all_pages('logs', region, self.session, 'describe_metric_filters',
                                                      'metricFilters')
        except Exception as e:
            print_exception('Failed to get CloudWatch metric filters: {}'.format(e))
            return []

    async def get_event_bus(self, region):
        client = AWSFacadeUtils.get_client('events', self.session, region)
        try:
            return await run_concurrently(
                lambda: client.describe_event_bus())
        except Exception as e:
            print_exception(f'Failed to describe event bus: {e}')

    async def has_event_rules(self, region):
        client = AWSFacadeUtils.get_client('events', self.session, region)
        try:
            return True if len(await run_concurrently(
                lambda: client.list_rules()['Rules'])) != 0 else False
        except Exception as e:
            print_exception(f'Failed to describe event rules: {e}')
