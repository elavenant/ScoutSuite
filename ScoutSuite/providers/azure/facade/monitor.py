from azure.mgmt.monitor import MonitorManagementClient

from ScoutSuite.core.console import print_exception
from ScoutSuite.providers.utils import run_concurrently, get_and_set_concurrently
from ScoutSuite.utils import get_user_agent


class MonitorFacade:
    def __init__(self, credentials):
        self.credentials = credentials

    def get_client(self, subscription_id: str):
        client = MonitorManagementClient(self.credentials.get_credentials('arm'),
                                        subscription_id=subscription_id)
        client._client.config.add_user_agent(get_user_agent())

    async def get_activity_logs(self, monitor, subscription_id: str):
        client = MonitorManagementClient(self.credentials.arm_credentials, subscription_id)
        client._client.config.add_user_agent(get_user_agent())

        try:
            return await run_concurrently(
                lambda: list(client.activity_log_alerts.list_by_subscription_id(subscription_id)
            ))
        except Exception as e:
            print_exception(f'Failed to retrieve activity logs alerts: {e}')
            return []
