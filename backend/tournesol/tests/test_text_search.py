from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from tournesol.entities.candidate import TYPE_CANDIDATE
from tournesol.entities.video import TYPE_VIDEO
from tournesol.models import Poll
from tournesol.models.poll import ALGORITHM_MEHESTAN
from tournesol.tests.factories.entity import EntityFactory, UserFactory, VideoFactory
from tournesol.tests.factories.entity_score import EntityCriteriaScoreFactory
from tournesol.tests.factories.poll import PollWithCriteriasFactory
from tournesol.tests.factories.ratings import (
    ContributorRatingCriteriaScoreFactory,
    ContributorRatingFactory,
)


class TextSearchTestCase(TestCase):
    """
    The text search can be used by multiple recommendations views,
    such as polls recommendations, and contributor recommendations.
    It can also be used for multiple polls.

    Its purpose is to filter some results based on textual input.
    It is currently based on the PostgreSQL full-text search.

    The tests are based on many design choices, that are likely to
    change over time.
    """

    def setUp(self):
        self.poll = Poll.default_poll()
        # Ranking based on relevance and scores is implemented for Mehestan only
        self.poll.algorithm = ALGORITHM_MEHESTAN
        self.poll.save()

        self.query = "fruit"

        self.text = "10 best fruit cake recipes"
        self.unrelated_text = "This sentence will contain no common word with the query"

        self.language = "en"

        self.url_base = f"/polls/{self.poll.name}/recommendations/"
        self.url_with_params = self.url_base + \
                   f"?metadata[language]={self.language}&search={self.query}"

        self.client = APIClient()
        self.user = UserFactory()

        self.setup_score = 5.0
        self.setup_entity = self._create_rated_entity(
            field1=self.text,
            criteria_score=self.setup_score,
        )
        self._create_rated_entity(field1=self.unrelated_text, criteria_score=self.setup_score)

        self.setup_results_count = 1

    def _create_rated_entity(self,
                             poll=None,
                             language="en",
                             field1="", field2="", field3="", field4="",
                             rated_criteria=None,
                             criteria_score=1.0,
                             unsafe=False):
        """
        Helper function to create a rated entity, with an indexed metadata.

        The metadata text fields contain the text indexed for the search.
        They depend on the entity type. Their weights are arbitrarily
        fixed in update_search_vector.

        Also creates criteria scores, since they are used for the
        calculation of the "total score" (= weighted score), which is
        used in the calculation of the search score (which determines
        the order in which the responses are displayed). These are
        positive by default, to avoid the entities being
        filtered as unsafe.
        """
        if not poll:
            poll = Poll.default_poll()

        if not rated_criteria:
            rated_criteria = poll.criterias_list

        nb_contributors = 0 if unsafe else 10

        if poll.entity_type == TYPE_VIDEO:
            entity = VideoFactory(
                metadata__name=field1,
                metadata__uploader=field2,
                metadata__tags=field3,
                metadata__description=field4,
                metadata__language=language,
                tournesol_score=10.0,
                rating_n_contributors=nb_contributors,
            )
        elif poll.entity_type == TYPE_CANDIDATE:
            metadata = {
                "name": field1,
                "frwiki_title": field2,
                "youtube_channel_id": field3,
                "twitter_username": field4,
            }
            entity = EntityFactory(
                type=TYPE_CANDIDATE,
                metadata=metadata,
                tournesol_score=10.0,
                rating_n_contributors=nb_contributors,
            )
        else:
            raise Exception("Unknown entity type")

        rating = ContributorRatingFactory(user=self.user, entity=entity, is_public=True)

        for criteria in rated_criteria:
            EntityCriteriaScoreFactory(
                poll=poll,
                entity=entity,
                criteria=criteria,
                score=criteria_score,
            )
            ContributorRatingCriteriaScoreFactory(
                contributor_rating=rating,
                criteria=criteria,
                score=criteria_score,
            )

        return entity
            
    def _make_url(self, search_query, language="en"):
        return self.url_base + f"?metadata[language]={language}&search={search_query}"

    def test_videos_are_searchable_by_metadata(self):
        """
        Test that the 4 text fields can be used for full-text search.
        Most of the tests, including this one, are on the default poll.

        (videos and candidates both have 4 indexed metadata fields, but
        there could be more on less than that with future entity types)
        """
        self._create_rated_entity(field1=self.text)
        self._create_rated_entity(field2=self.text)
        self._create_rated_entity(field3=self.text)
        self._create_rated_entity(field4=self.text)

        response = self.client.get(self.url_with_params, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 4 + self.setup_results_count)

    def test_search_by_uid(self):
        """
        Check that the uid (e.g. "yt:GuTgfnkILGs" or just "GuTgfnkILGs")
        can be used for the text search.
        """
        self.setup_entity.uid = "yt:GuTgfnkILGs"
        self.setup_entity.save()

        response = self.client.get(self._make_url("yt:GuTgfnkILGs"), format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

        response = self.client.get(self._make_url("GuTgfnkILGs"), format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_candidates_are_searchable_by_metadata(self):
        """
        The text search is not very useful for candidates,
        but verify anyway that it is functional.
        """
        poll = PollWithCriteriasFactory(entity_type=TYPE_CANDIDATE)
        candidate = "Bertrand Usclat"
        other_candidate = "Anne Hidalgo"
        query = "bertrand"

        self._create_rated_entity(poll=poll, field1=candidate)
        self._create_rated_entity(poll=poll, field2=candidate)
        self._create_rated_entity(poll=poll, field3=candidate)
        self._create_rated_entity(poll=poll, field4=candidate)
        self._create_rated_entity(poll=poll, field1=other_candidate)

        response = self.client.get(
            f"/polls/{poll.name}/recommendations/?search={query}",
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 4)

    def test_private_contributor_recommendations(self):
        """
        Verify that the full-text search works for private
        contributor recommendations
        """
        self.client.force_authenticate(self.user)

        self._create_rated_entity(field1=self.text)
        self._create_rated_entity(field1=self.unrelated_text)

        response = self.client.get(
            f"/users/me/recommendations/{self.poll.name}"
            f"?search={self.query}&metadata[language]={self.language}",
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1 + self.setup_results_count)

    def test_public_contributor_recommendations(self):
        """
        Verify that the full-text search works for public
        contributor recommendations
        """
        self._create_rated_entity(field1=self.text)
        self._create_rated_entity(field1=self.unrelated_text)

        response = self.client.get(
            f"/users/{self.user.username}/recommendations/{self.poll.name}"
            f"?search={self.query}&metadata[language]={self.language}",
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1 + self.setup_results_count)


    def test_stop_words(self):
        """
        The words that carry no meaning ("stop words") should be
        automatically removed by Postgres. In a language-dependent way.
        """
        query = "cake and so my the he again been"

        self._create_rated_entity(field1="and so my the he again been")

        response = self.client.get(
            self._make_url(query),
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], self.setup_results_count)

        self._create_rated_entity(field1="cake")

        response = self.client.get(
            self._make_url(query),
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1 + self.setup_results_count)

    def test_stop_words_french(self):
        """
        Each language has its stop words dictionary.
        Check that it works for french too.
        """
        query = "oignon le ma elle du où"

        self._create_rated_entity(field1="le ma elle du où", language="fr")

        response = self.client.get(
            self._make_url(query, "fr"),
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

        self._create_rated_entity(field1="oignon", language="fr")

        response = self.client.get(
            self._make_url(query, "fr"),
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)


    def test_stemming(self):
        """
        Only the root of words is indexed or queried.
        This allows to match other words that have the same root,
        and thus usually the same meaning.
        """
        word = "fruitful"
        query = "fruits"
        self._create_rated_entity(field1=word)

        response = self.client.get(
            self._make_url(query),
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], self.setup_results_count + 1)

    def test_stemming_french(self):
        """
        Each language has its stemming dictionary.
        Check that it works for french too.
        """
        word = "construction"
        query = "constructif"
        self._create_rated_entity(field1=word, language="fr")

        response = self.client.get(
            self._make_url(query, "fr"),
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_languages_filter(self):
        """
        Only entities matching the query languages must be returned.
        """
        self._create_rated_entity(field1=self.text, language="fr")
        self._create_rated_entity(field1=self.text, language="fr")

        response = self.client.get(self.url_with_params, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], self.setup_results_count)

    def test_multiple_languages(self):
        """
        If the recommendation filter includes multiple languages,
        each entity should have a relevance score equal to the
        max relevance score over all languages.
        """
        self._create_rated_entity(field1=self.text, language="en")
        self._create_rated_entity(field1=self.text, language="fr")

        response = self.client.get(
            self.url_base + f"?metadata[language]=en&metadata[language]=fr&search={self.query}",
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2 + self.setup_results_count)

    def test_languages_unknown_by_postgres(self):
        """
        Postgres full-text search does not support as many languages
        as the Tournesol query languages filter.

        If all the languages of the query are not supported by Postgres,
        a classic case-insensitive, language-independent search is done.

        Just check that the search still works.
        """
        word = "kook"
        language_unknown_by_postgres = "et"  # Estonian
        other_language_not_supported = "mk"  # Macedonian
        self._create_rated_entity(field1=word, language=language_unknown_by_postgres)
        self._create_rated_entity(field1=word, language=other_language_not_supported)
        self._create_rated_entity(field1=word, language="fr")

        response = self.client.get(
            self._make_url(word, "et"),
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_no_language_filter(self):
        """
        The results in every language should be returned
        """
        word = "kook"
        self._create_rated_entity(field1=word, language="et")
        self._create_rated_entity(field1=word, language="mk")
        self._create_rated_entity(field1=word, language="fr")

        response = self.client.get(
            self.url_base + "?search=" + word,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)

    def test_sorting_depends_on_total_score(self):
        """
        If the relevance is the same, the results with higher
        total score (or "weighted score") should appear first.
        """
        scores = [.3, -4.7, 6.0, 0.0, 8.1, -10.0, -2.4, -2.3, 1.2, 1.1]
        entities = []
        for score in scores:
            entities.append(self._create_rated_entity(field1=self.text, criteria_score=score))

        entities = [self.setup_entity] + entities
        scores = [self.setup_score] + scores
        self.assertEqual(len(scores), len(entities))

        response = self.client.get(self.url_with_params + "&unsafe=true", format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], len(scores))
        self.assertEqual(len(response.data["results"]), response.data["count"])

        sorted_scores = sorted(scores, reverse=True)
        for index, score in enumerate(sorted_scores):
            entity = entities[scores.index(score)]
            self.assertEqual(response.data["results"][index]["uid"], entity.uid)

    def test_public_contributor_recommendations_sorting_depends_on_total_score(self):
        """
        Same test as above, but for public contributor recommendations.
        """
        scores = [.3, -4.7, 6.0, 0.0, 8.1, -10.0, -2.4, -2.3, 1.2, 1.1]
        entities = []
        for score in scores:
            entities.append(self._create_rated_entity(field1=self.text, criteria_score=score))

        entities = [self.setup_entity] + entities
        scores = [self.setup_score] + scores
        self.assertEqual(len(scores), len(entities))

        response = self.client.get(
            f"/users/{self.user.username}/recommendations/{self.poll.name}"
            f"?search={self.query}&metadata[language]={self.language}",
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], len(scores))
        self.assertEqual(len(response.data["results"]), response.data["count"])

        sorted_scores = sorted(scores, reverse=True)
        for index, score in enumerate(sorted_scores):
            entity = entities[scores.index(score)]
            self.assertEqual(response.data["results"][index]["uid"], entity.uid)

    def test_private_contributor_recommendations_sorting_depends_on_total_score(self):
        """
        Same test as above, but for private contributor recommendations.
        """
        scores = [.3, -4.7, 6.0, 0.0, 8.1, -10.0, -2.4, -2.3, 1.2, 1.1]
        entities = []
        for score in scores:
            entities.append(self._create_rated_entity(field1=self.text, criteria_score=score))

        entities = [self.setup_entity] + entities
        scores = [self.setup_score] + scores
        self.assertEqual(len(scores), len(entities))

        self.client.force_authenticate(self.user)
        response = self.client.get(
            f"/users/me/recommendations/{self.poll.name}"
            f"?search={self.query}&metadata[language]={self.language}",
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], len(scores))
        self.assertEqual(len(response.data["results"]), response.data["count"])

        sorted_scores = sorted(scores, reverse=True)
        for index, score in enumerate(sorted_scores):
            entity = entities[scores.index(score)]
            self.assertEqual(response.data["results"][index]["uid"], entity.uid)

    def test_videos_fields_weights(self):
        """
        The words in each text field do not carry the same importance.
        e.g., the words in the title are more important than
        those in the descriptions.

        In the function update_search_vector, each text field is
        associated with a weight.

        In Postgres, there are only 4 type of weights ("A", "B", "C", "D"),
        which have by default the value (1.0, 0.4, 0.2, 0.1). The only
        thing that should be tested here is that finding the searched
        word in a highly weighted field (e.g. "A") gives a higher
        relevance.

        For videos, the field 1 ("name") is more highly weighted than the
        field 4 ("description"). The video matched on field 4 should
        appear in 2nd position (even if it's score is slightly higher).
        """
        other_entity = self._create_rated_entity(
            field4=self.text,
            criteria_score=self.setup_score + 0.1,
        )

        response = self.client.get(self.url_with_params, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(response.data["results"][0]["uid"], self.setup_entity.uid)
        self.assertEqual(response.data["results"][1]["uid"], other_entity.uid)

    def test_query_weights(self):
        """
        The weights should influence the total_score, which
        should influence the sorting order.
        """
        query = "onion"
        field = "how to cook an onion cake"
        criteria_1 = self.poll.criterias_list[0]
        criteria_2 = self.poll.criterias_list[1]

        # Check that the relevance compensates for the lower score
        entity_1 = self._create_rated_entity(
            field1=field,
            criteria_score=1.0,
            rated_criteria=[criteria_1]
        )
        entity_2 = self._create_rated_entity(
            field1=field,
            criteria_score=2.0,
            rated_criteria=[criteria_1, criteria_2]
        )

        EntityCriteriaScoreFactory(
            poll=self.poll,
            entity=entity_1,
            criteria=criteria_2,
            score=3.0,
        )

        response = self.client.get(
            self._make_url(query),
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(response.data["results"][0]["uid"], entity_2.uid)
        self.assertEqual(response.data["results"][1]["uid"], entity_1.uid)

        response = self.client.get(
            self._make_url(query) + f"&weights[{criteria_1}]=10&weights[{criteria_2}]=50",
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(response.data["results"][0]["uid"], entity_1.uid)
        self.assertEqual(response.data["results"][1]["uid"], entity_2.uid)

    def test_multiple_matches(self):
        """
        If the word appears twice in a text field, it should give a higher
        score than if it appears only once.
        """
        query = "onion"
        relevant_text = "how to cook an onion cake with onions"
        less_relevant_text = "how to cook an onion cake"
        unrelated_text = "how to build a house"

        # Check that the relevance compensates for the lower score
        relevant_entity = self._create_rated_entity(field1=relevant_text, criteria_score=1.0)
        less_relevant_entity = self._create_rated_entity(
            field1=less_relevant_text,
            criteria_score=1.1
        )
        self._create_rated_entity(field1=unrelated_text, criteria_score=1.2)

        response = self.client.get(
            self._make_url(query),
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(response.data["results"][0]["uid"], relevant_entity.uid)
        self.assertEqual(response.data["results"][1]["uid"], less_relevant_entity.uid)

    def test_public_contributor_recommendations_multiple_matches(self):
        """
        If the word appears twice in a text field, it should give a higher
        score than if it appears only once.
        """
        query = "onion"
        relevant_text = "how to cook an onion cake with onions"
        less_relevant_text = "how to cook an onion cake"
        unrelated_text = "how to build a house"

        # Check that the relevance compensates for the lower score
        relevant_entity = self._create_rated_entity(field1=relevant_text, criteria_score=1.0)
        less_relevant_entity = self._create_rated_entity(
            field1=less_relevant_text,
            criteria_score=1.1
        )
        self._create_rated_entity(field1=unrelated_text, criteria_score=1.2)

        response = self.client.get(
            f"/users/{self.user.username}/recommendations/{self.poll.name}"
            f"?search={query}&metadata[language]={self.language}",
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(response.data["results"][0]["uid"], relevant_entity.uid)
        self.assertEqual(response.data["results"][1]["uid"], less_relevant_entity.uid)

    def test_private_contributor_recommendations_multiple_matches(self):
        """
        If the word appears twice in a text field, it should give a higher
        score than if it appears only once.
        """
        query = "onion"
        relevant_text = "how to cook an onion cake with onions"
        less_relevant_text = "how to cook an onion cake"
        unrelated_text = "how to build a house"

        # Check that the relevance compensates for the lower score
        relevant_entity = self._create_rated_entity(field1=relevant_text, criteria_score=1.0)
        less_relevant_entity = self._create_rated_entity(
            field1=less_relevant_text,
            criteria_score=1.1
        )
        self._create_rated_entity(field1=unrelated_text, criteria_score=1.2)

        self.client.force_authenticate(self.user)
        response = self.client.get(
            f"/users/me/recommendations/{self.poll.name}"
            f"?search={query}&metadata[language]={self.language}",
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(response.data["results"][0]["uid"], relevant_entity.uid)
        self.assertEqual(response.data["results"][1]["uid"], less_relevant_entity.uid)

    def test_multiple_words(self):
        """
        Test with multiple words in the query.
        
        Consider that if any of the 2 query words is not in
        the text field, the entity should not be returned.
        """
        sentence_query = "onion sauce"
        relevant_text = "how to cook an onion sauce"
        less_relevant_text = "how to cook an onion cake"
        unrelated_text = "how to build a house"

        # Check that the relevance compensates for the lower score
        relevant_entity = self._create_rated_entity(field1=relevant_text, criteria_score=1.0)
        self._create_rated_entity(field1=less_relevant_text, criteria_score=1.1)
        self._create_rated_entity(field1=unrelated_text, criteria_score=1.2)

        response = self.client.get(
            self._make_url(sentence_query),
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["uid"], relevant_entity.uid)

    def test_case_insensitive(self):

        word = "fRuIt"
        query = "FrUiT"
        self._create_rated_entity(field1=word)

        response = self.client.get(
            self._make_url(query),
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], self.setup_results_count + 1)


    def test_accents_insensitive(self):
        """
        The search should ignore accents to be more user-friendly.
        Here one "accent" is missing both in the query and the text field.

        This is done by creating a specific Postgres full-text search
        configuration for each language ("customized_french" here)
        with the "unaccent" filter dictionary.
        """
        word = "œillere"
        query = "oeillère"
        self._create_rated_entity(field1=word, language="fr")

        response = self.client.get(
            self._make_url(query, "fr"),
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_parse_newlines_in_metadata(self):
        description = "how to cook an onion cake\ningredients :\nonions"
        query = "ingredient"
        self._create_rated_entity(field1=description)

        response = self.client.get(
            self._make_url(query),
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_unsafe_filter(self):
        """
        Check that videos that have a negative score are
        still filtered correctly.
        """
        self._create_rated_entity(field1=self.text, unsafe=True)

        response = self.client.get(self.url_with_params, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], self.setup_results_count)

        response = self.client.get(self.url_with_params + "&unsafe=true", format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], self.setup_results_count + 1)
