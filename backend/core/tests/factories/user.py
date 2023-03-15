import factory

from core.models import User


class UserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = User

    email = factory.LazyAttributeSequence(
        lambda a, n: '{}.{}.{}@example.com'.format(a.first_name, a.last_name, n).lower()
    )
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    username = factory.Sequence(lambda n: 'username %s' % n)
