import namegenerator
import names
import numpy as np


class PreferenceDataset(object):
    """Preference dataset abstract class."""

    def __init__(self, objects, users, fields, ratings=None,
                 n_ratings=10):
        self.objects = objects
        self.users = users
        self.fields = fields
        if ratings is not None:
            self.ratings = ratings
        else:
            self._generate_many(n_ratings=n_ratings)

    def _generate_many(self, n_ratings=10):
        self.ratings = [self._generate_one() for _ in range(n_ratings)]

    def _generate_one(self):
        r = self._generate_one_impl()
        for x in ['o1', 'o2', 'ratings', 'user']:
            assert x in r, "Missing field %s" % x
        assert r['o1'] in self.objects, "Object not found %s" % r['o1']
        assert r['o2'] in self.objects, "Object not found %s" % r['o2']
        assert r['user'] in self.users, "Object not found %s" % r['user']
        for f in self.fields:
            assert f in r['ratings'], "Field not found %s" % f
            assert 0 <= r['ratings'][f] <= 100, "Value must be in [0, 100] %s %s" \
                                                % (f, str(r['ratings'][f]))
        return r

    def _generate_one_impl(self):
        raise NotImplementedError("This class is abstract")

    def __repr__(self):
        return "<PrefDataset %s~objects[%d] %s~fields[%d] %s~users[%d] %s~ratings[%d]" % \
               (np.random.choice(self.objects), len(self.objects),
                np.random.choice(self.fields), len(self.fields),
                np.random.choice(self.users), len(self.users),
                np.random.choice(self.ratings), len(self.ratings))


class ToyRandomDataset(PreferenceDataset):
    """Random dataset."""

    def __init__(self, n_objects=10, n_users=10):
        # list of objects to consider
        objects = [namegenerator.gen() for _ in range(n_objects)]

        # fields to consider (features)
        fields = [
            "unicorniness",
            "magic_skills",
            "number_of_trump_appearances"]

        # some users
        users = [names.get_full_name() for _ in range(n_users)]

        super(ToyRandomDataset, self).__init__(objects=objects,
                                               fields=fields,
                                               users=users)

    def _generate_one_impl(self):
        """Sample one rating."""
        o1, o2 = None, None
        while o1 == o2:
            o1 = np.random.choice(self.objects)
            o2 = np.random.choice(self.objects)

        def get_rating():
            return np.random.uniform(low=0, high=100)

        user = np.random.choice(self.users)
        ratings = {f: get_rating() for f in self.fields}
        return {'o1': o1, 'o2': o2, 'ratings': ratings,
                'user': user}


class ToyHardcodedDataset(PreferenceDataset):
    """Random dataset."""

    def __init__(self):
        users = ['sergei', 'le']
        objects = ['trump_video', 'science4all_video', 'bbc_video']
        fields = ['accuracy', 'pedagogy']

        self.scores_dict = \
            {'sergei':
                {
                    'accuracy':
                        {('trump_video', 'science4all_video'): 90,
                         ('trump_video', 'bbc_video'): 85,
                         ('science4all_video', 'bbc_video'): 0
                         },
                    'pedagogy':
                        {('trump_video', 'science4all_video'): 100,
                         ('trump_video', 'bbc_video'): 71,
                         ('science4all_video', 'bbc_video'): 1
                         },
                },
                'le':
                    {
                        'accuracy':
                            {('trump_video', 'science4all_video'): 99,
                             ('trump_video', 'bbc_video'): 80,
                             ('science4all_video', 'bbc_video'): 10
                             },
                        'pedagogy':
                            {('trump_video', 'science4all_video'): 100,
                             ('trump_video', 'bbc_video'): 70,
                             ('science4all_video', 'bbc_video'): 0
                             },
                }
             }

        super(ToyHardcodedDataset, self).__init__(objects=objects,
                                                  fields=fields,
                                                  users=users)

    def _generate_one_impl(self):
        """Sample one rating."""
        o1, o2 = None, None
        user = np.random.choice(self.users)
        while o1 == o2:
            o1 = np.random.choice(self.objects)
            o2 = np.random.choice(self.objects)

        def get_rating(f):
            scores = self.scores_dict[user]

            if (o1, o2) in scores[f]:
                return scores[f][(o1, o2)]
            elif (o2, o1) in scores[f]:
                return 100 - scores[f][(o2, o1)]
            else:
                raise Exception("score not found")

        ratings = {f: get_rating(f) for f in self.fields}
        return {'o1': o1, 'o2': o2, 'ratings': ratings,
                'user': user}
