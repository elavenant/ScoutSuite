import datetime

from azure.mgmt.keyvault import KeyVaultManagementClient
from azure.mgmt.monitor import MonitorManagementClient

from ScoutSuite.core.console import print_exception
from ScoutSuite.providers.utils import run_concurrently, get_and_set_concurrently
from ScoutSuite.utils import get_user_agent


class KeyVaultFacade:

    def __init__(self, credentials):
        self.credentials = credentials

    def get_client(self, subscription_id: str):
        client = KeyVaultManagementClient(self.credentials.get_credentials('arm'),
                                        subscription_id=subscription_id)
        client._client.config.add_user_agent(get_user_agent())
        return client

    async def get_key_vaults(self, subscription_id: str):
        try:
            client = self.get_client(subscription_id)
            keyvaults =  await run_concurrently(
                lambda: list(client.vaults.list_by_subscription()))
        except Exception as e:
            print_exception(f'Failed to retrieve key vaults: {e}')
            return []
        else:
            await get_and_set_concurrently([self._get_and_set_diagnostic_settings], keyvaults,
                                           subscription_id=subscription_id)
            return keyvaults

    async def _get_and_set_diagnostic_settings(self, keyvault, subscription_id: str):
        client = MonitorManagementClient(self.credentials.arm_credentials, subscription_id)
        client._client.config.add_user_agent(get_user_agent())

        try:
            diagnostic_settings = await run_concurrently(
                lambda: list(client.diagnostic_settings.list(keyvault["id"])
            ))
        except Exception as e:
            print_exception(f'Failed to retrieve diagnostic settings: {e}')
            setattr(keyvault, 'diagnostic_settings', [])
        else:
            setattr(keyvault, 'diagnostic_settings', diagnostic_settings)