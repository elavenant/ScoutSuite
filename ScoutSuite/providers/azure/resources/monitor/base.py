from ScoutSuite.providers.azure.resources.subscriptions import Subscriptions

from .ActivityLogs import ActivityLogs


class Monitor(Subscriptions):
    _children = [
        (ActivityLogs, 'activity_logs')
    ]
