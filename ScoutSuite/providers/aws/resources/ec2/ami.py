from ScoutSuite.providers.aws.resources.base import AWSResources
from ScoutSuite.providers.aws.facade.base import AWSFacade


class AmazonMachineImages(AWSResources):
    def __init__(self, facade: AWSFacade, region: str):
        super().__init__(facade)
        self.region = region

    async def fetch_all(self):
        raw_images = await self.facade.ec2.get_images(self.region)
        for raw_image in raw_images:
            print("raw_image :",  raw_image)
            name, resource = self._parse_image(raw_image)
            self[name] = resource

    def _parse_image(self, raw_image):
        raw_image['id'] = raw_image.get('ImageId')
        raw_image['name'] = raw_image.get('Name')
        raw_image['arn'] = 'arn:aws:ec2:{}:{}:ami/{}'.format(self.region,
                                                            raw_image.get('OwnerId'),
                                                            raw_image.get('ImageId'))
        return raw_image['id'], raw_image
