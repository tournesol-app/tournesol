from django.test import TestCase

from tournesol.models.entity_context import EntityContext
from tournesol.tests.factories.entity import VideoFactory
from tournesol.tests.factories.poll import PollWithCriteriasFactory


class PollTestCase(TestCase):
    def setUp(self):
        self.poll1 = PollWithCriteriasFactory(name="poll1", entity_type="video")
        self.poll2 = PollWithCriteriasFactory(name="poll2", entity_type="video")

    def test_entity_has_unsafe_context(self):
        """
        The `entity_has_unsafe_context` method should return True only when:
        there is at least one matching context enabled, unsafe, and attached
        to the given poll.
        """
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

        # Enabled and unsafe context.
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

    def test_entity_has_unsafe_context_no_context(self):
        video = VideoFactory()
        unsafe, origin = self.poll1.entity_has_unsafe_context(video.metadata)
        self.assertEqual(unsafe, False)
        self.assertEqual(origin, None)

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

    def test_get_entity_contexts(self):
        """
        The `get_entity_contexts` method should return a list of all enabled
        matching contexts, attached to the given poll.
        """
        video = VideoFactory()

        # Safe context.
        entity_context = EntityContext.objects.create(
            name="context_safe",
            origin=EntityContext.ASSOCIATION,
            predicate={"uploader": video.metadata["uploader"]},
            unsafe=False,
            enabled=True,
            poll=self.poll1,
        )

        contexts = self.poll1.get_entity_contexts(video.metadata)
        self.assertEqual(len(contexts), 1)
        self.assertEqual(contexts[0].pk, entity_context.pk)

        EntityContext.objects.all().delete()
        # Unsafe context.
        entity_context = EntityContext.objects.create(
            name="context_unsafe",
            origin=EntityContext.ASSOCIATION,
            predicate={"uploader": video.metadata["uploader"]},
            unsafe=True,
            enabled=True,
            poll=self.poll1,
        )

        contexts = self.poll1.get_entity_contexts(video.metadata)
        self.assertEqual(len(contexts), 1)
        self.assertEqual(contexts[0].pk, entity_context.pk)

        EntityContext.objects.all().delete()
        # Disabled contexts.
        EntityContext.objects.create(
            name="context_safe_disabled",
            origin=EntityContext.ASSOCIATION,
            predicate={"uploader": video.metadata["uploader"]},
            unsafe=False,
            enabled=False,
            poll=self.poll1,
        )
        EntityContext.objects.create(
            name="context_unsafe_disabled",
            origin=EntityContext.ASSOCIATION,
            predicate={"uploader": video.metadata["uploader"]},
            unsafe=True,
            enabled=False,
            poll=self.poll1,
        )

        contexts = self.poll1.get_entity_contexts(video.metadata)
        self.assertEqual(contexts, [])

    def test_get_entity_contexts_no_context(self):
        video = VideoFactory()
        contexts = self.poll1.get_entity_contexts(video.metadata)
        self.assertEqual(contexts, [])

    def test_get_entity_contexts_poll_specific(self):
        """
        The method `get_entity_contexts` should be limited to the poll
        instance.
        """
        video = VideoFactory()

        EntityContext.objects.create(
            name="context_safe",
            origin=EntityContext.ASSOCIATION,
            predicate={"uploader": video.metadata["uploader"]},
            unsafe=False,
            enabled=True,
            poll=self.poll2,
        )

        contexts = self.poll1.get_entity_contexts(video.metadata)
        self.assertEqual(contexts, [])
