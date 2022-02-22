from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response

from tournesol.models import Poll


class PollScopedViewMixin:
    """
    A mixin view that automatically retrieves the poll name from a URL path
    parameter, and make it available in the view and the serializer context.

    This view must be mixed with a `rest_framework.generics.GenericAPIView`
    view or a subclass of it.
    """
    poll_parameter = "poll_name"
    # used to avoid multiple similar database queries in a single HTTP request
    poll_from_url: Poll

    def poll_from_kwargs_or_404(self, request_kwargs):
        try:
            return Poll.objects.get(name=request_kwargs[self.poll_parameter])
        except ObjectDoesNotExist:
            return self.response_404_poll_doesnt_exist(request_kwargs[self.poll_parameter])

    def response_404_poll_doesnt_exist(self, poll_name: str):
        return Response(
            {
                "detail": "The requested poll {0} doesn't exist.".format(poll_name),
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    def initial(self, request, *args, **kwargs):
        """
        Runs anything that needs to occur prior to calling the method handler.
        """
        super().initial(request, *args, **kwargs)

        # make the requested poll available at any time in the view
        self.poll_from_url = self.poll_from_kwargs_or_404(kwargs)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["poll"] = self.poll_from_url
        return context
