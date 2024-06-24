import yaml
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient


class OpenAPISchemaTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_schema_ok(self):
        resp = self.client.get("/schema/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_schema_nullable_field(self):
        resp = self.client.get("/schema/")

        # TODO: check the relevance of this test
        #
        # 'language' in model VideoWithCriteriaScore should appear as nullable.
        # This attribute used to be lost because of how DRF handles read-only fields.
        # schema = yaml.safe_load(resp.content)
        # video_model = schema["components"]["schemas"]["VideoSerializerWithCriteria"]
        # self.assertEqual(video_model["properties"]["language"]["nullable"], True)
