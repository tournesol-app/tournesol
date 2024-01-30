from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import NotFound

from tournesol.models import Poll


class PollScopedViewMixin:
    """
    A mixin view that automatically retrieves the poll name from a URL path
    parameter, and make it available in the view and the serializer context.

    This view must be mixed with a `rest_framework.generics.GenericAPIView`
    view or a subclass of it.
    """

    entity_contexts = None
    enable_entity_contexts = False

    poll_parameter = "poll_name"
    # used to avoid multiple similar database queries in a single HTTP request
    poll_from_url: Poll

    @staticmethod
    def get_entity_contexts(poll: Poll):
        return poll.all_entity_contexts.prefetch_related("texts").all()

    def poll_from_kwargs_or_404(self, request_kwargs):
        poll_name = request_kwargs[self.poll_parameter]
        try:
            return Poll.objects.get(name=poll_name)
        except ObjectDoesNotExist as error:
            raise NotFound(f"The requested poll {poll_name} doesn't exist.") from error

    def initial(self, request, *args, **kwargs):
        """
        Runs anything that needs to occur prior to calling the method handler.
        """
        super().initial(request, *args, **kwargs)

        # make the requested poll available at any time in the view
        self.poll_from_url = self.poll_from_kwargs_or_404(kwargs)

        if self.enable_entity_contexts:
            self.entity_contexts = self.get_entity_contexts(self.poll_from_url)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["poll"] = self.poll_from_url
        context["entity_contexts"] = self.entity_contexts
        return context
