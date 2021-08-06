from ScoutSuite.providers.azure.facade.base import AzureFacade
from ScoutSuite.providers.azure.resources.base import AzureResources
from ScoutSuite.providers.utils import get_non_provider_id
from ScoutSuite.providers.azure.utils import get_resource_group_name


class ActivityLogs(AzureResources):

    def __init__(self, facade: AzureFacade, subscription_id: str):
        super().__init__(facade)
        self.subscription_id = subscription_id

    async def fetch_all(self):
        for raw_activity in await self.facade.monitor.get_activity_logs(self.subscription_id):
            id, activity = self._parse_web_app(raw_activity)
            self[id] = activity

    def _parse_activity_logs(self, raw_activity):
        activity = {}

        activity["actions"] = raw_activity.Actions
        activity["condition"] = raw_activity.Condition
        activity["description"] = raw_activity.Description
        activity["enabled"] = raw_activity.Enabled
        activity["id"] = raw_activity.Id
        activity["kind"] = raw_activity.Kind
        activity["location"] = raw_activity.Location
        activity["name"] = raw_activity.Name
        activity["scopes"] = raw_activity.Scopes
        activity["type"] = raw_activity.Type
        activity["operation_name_list"] = self._get_operation_name_list(raw_activity)
        if raw_activity.tags is not None:
            activity['tags'] = ["{}:{}".format(key, value) for key, value in raw_activity.tags.items()]
        else:
            activity['tags'] = []

        return activity

    def _get_operation_name_list(self, activity):
        res = []
        for condition in activity.Condition.AllOf:
            if condition.Field == "operationName":
                res.append(condition.Equals)
        return res


