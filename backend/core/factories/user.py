import factory

from core.models import User


class UserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = User

    email = factory.LazyAttribute(
        lambda a: '{}.{}@example.com'.format(a.first_name, a.last_name).lower()
    )
    first_name = factory.Sequence(lambda n: 'first name %s' % n)
    last_name = factory.Sequence(lambda n: 'last name %s' % n)
    username = factory.Sequence(lambda n: 'username %s' % n)
