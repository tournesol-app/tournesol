from django.test import TestCase

from tournesol.models.entity_context import EntityContext
from tournesol.tests.factories.entity import VideoFactory
from tournesol.tests.factories.poll import PollWithCriteriasFactory


class PollTestCase(TestCase):
    def setUp(self):
        self.poll1 = PollWithCriteriasFactory(name="poll1", entity_type="video")
        self.poll2 = PollWithCriteriasFactory(name="poll2", entity_type="video")

    def test_entity_has_unsafe_context_no_context(self):
        video = VideoFactory()
        unsafe, origin = self.poll1.entity_has_unsafe_context(video.metadata)
        self.assertEqual(unsafe, False)
        self.assertEqual(origin, None)

    def test_entity_has_unsafe_context(self):
        video = VideoFactory()

        # Safe context.
        EntityContext.objects.create(
            name="context_safe",
            origin=EntityContext.ASSOCIATION,
            predicate={"uploader": video.metadata["uploader"]},
            unsafe=False,
            enabled=True,
            poll=self.poll1,
        )

        unsafe, origin = self.poll1.entity_has_unsafe_context(video.metadata)
        self.assertEqual(unsafe, False)
        self.assertEqual(origin, None)

        # Disabled context.
        EntityContext.objects.create(
            name="context_unsafe_disabled",
            origin=EntityContext.ASSOCIATION,
            predicate={"uploader": video.metadata["uploader"]},
            unsafe=True,
            enabled=False,
            poll=self.poll1,
        )

        unsafe, origin = self.poll1.entity_has_unsafe_context(video.metadata)
        self.assertEqual(unsafe, False)
        self.assertEqual(origin, None)

        EntityContext.objects.create(
            name="context_unsafe_enabled",
            origin=EntityContext.ASSOCIATION,
            predicate={"uploader": video.metadata["uploader"]},
            unsafe=True,
            enabled=True,
            poll=self.poll1,
        )

        unsafe, origin = self.poll1.entity_has_unsafe_context(video.metadata)
        self.assertEqual(unsafe, True)
        self.assertEqual(origin, EntityContext.ASSOCIATION)

    def test_entity_has_unsafe_context_poll_specific(self):
        """
        The method `entity_has_unsafe_context` should be limited to the poll
        instance.
        """
        video = VideoFactory()

        EntityContext.objects.create(
            name="context_unsafe_enabled",
            origin=EntityContext.ASSOCIATION,
            predicate={"uploader": video.metadata["uploader"]},
            unsafe=True,
            enabled=True,
            poll=self.poll2,
        )

        unsafe, origin = self.poll1.entity_has_unsafe_context(video.metadata)
        self.assertEqual(unsafe, False)
        self.assertEqual(origin, None)
