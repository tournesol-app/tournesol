"""
All test cases of the `faq` views.
"""

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from faq.models import FAQAnswer, FAQAnswerLocale, FAQuestion, FAQuestionLocale


def create_question(name, rank, enabled):
    return FAQuestion.objects.create(name=name, rank=rank, enabled=enabled)


def create_answer(name, question):
    return FAQAnswer.objects.create(name=name, question=question)


class FAQuestionLocalizedListViewTestCase(TestCase):
    """
    TestCase of the `FAQuestionLocalizedListView` view.
    """

    default_lang = "en"
    available_lang = "fr"
    unavailable_lang = "zz"

    def setUp(self):
        self.client = APIClient()
        self.faq_base_url = "/faq/"

        self.question1 = create_question("i_dont_understand_why", 20, True)

        self.question1_loc_en = FAQuestionLocale.objects.create(
            question=self.question1,
            language=self.default_lang,
            text="I don't understand why.",
        )

        self.question1_loc_fr = FAQuestionLocale.objects.create(
            question=self.question1,
            language=self.available_lang,
            text="Je ne comprends pas pourquoi.",
        )

        self.answer1 = create_answer("i_dont_understand_why_ans", self.question1)

        self.answer1_loc_en = FAQAnswerLocale.objects.create(
            answer=self.answer1, language=self.default_lang, text="Tournesol aims to..."
        )

        self.answer1_loc_fr = FAQAnswerLocale.objects.create(
            answer=self.answer1,
            language=self.available_lang,
            text="Tournesol cherche à...",
        )

    def test_anon_200_list_language_unknown(self):
        """
        An anonymous user can access the FAQ.
        """
        response = self.client.get(self.faq_base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_faq_language_unknown(self):
        """
        When no HTTP Accept-Language header is present in the request, the
        `en` localization must be returned.
        """
        response = self.client.get(self.faq_base_url)
        results = response.data["results"]

        self.assertDictEqual(
            results[0],
            {
                "name": self.question1.name,
                "question": self.question1_loc_en.text,
                "answer": self.answer1_loc_en.text,
            },
        )

    def test_list_faq_language_unavailable(self):
        """
        When the requested localization is not available in the database, the
        `en` localization must be returned.
        """
        response = self.client.get(
            self.faq_base_url, HTTP_ACCEPT_LANGUAGE=self.unavailable_lang
        )
        results = response.data["results"]

        self.assertDictEqual(
            results[0],
            {
                "name": self.question1.name,
                "question": self.question1_loc_en.text,
                "answer": self.answer1_loc_en.text,
            },
        )

    def test_list_faq_language_available(self):
        """
        When a known language is requested, the matching localization must be
        returned.
        """
        response = self.client.get(
            self.faq_base_url, HTTP_ACCEPT_LANGUAGE=self.available_lang
        )
        results = response.data["results"]

        self.assertDictEqual(
            results[0],
            {
                "name": self.question1.name,
                "question": self.question1_loc_fr.text,
                "answer": self.answer1_loc_fr.text,
            },
        )

    def test_list_faq_question_without_answer(self):
        """
        A question without answer must not be returned by the API.
        """
        self.answer1.delete()

        response = self.client.get(self.faq_base_url)
        results = response.data["results"]
        self.assertListEqual(results, [])

    def test_list_faq_disabled_questions_dont_appear(self):
        """
        Disabled questions must not be returned by the API.
        """
        question = create_question("new_question", 1, True)
        create_answer("new_question", question)

        response = self.client.get(self.faq_base_url)
        self.assertEqual(len(response.data["results"]), 2)

        question.enabled = False
        question.save(update_fields=["enabled"])

        response = self.client.get(self.faq_base_url)
        self.assertEqual(len(response.data["results"]), 1)

    def test_list_faq_ordering(self):
        """
        The questions must be ordered by rank.
        """
        question = create_question("first_question", self.question1.rank - 1, True)
        create_answer("first_answer", question)

        response = self.client.get(self.faq_base_url)
        results = response.data["results"]

        self.assertDictEqual(
            results[0],
            {
                "name": "first_question",
                "question": "first_question",
                "answer": "first_answer",
            },
        )

        self.assertDictEqual(
            results[1],
            {
                "name": self.question1.name,
                "question": self.question1_loc_en.text,
                "answer": self.answer1_loc_en.text,
            },
        )

        question.rank = self.question1.rank + 1
        question.save(update_fields=["rank"])

        response = self.client.get(self.faq_base_url)
        results = response.data["results"]

        self.assertDictEqual(
            results[0],
            {
                "name": self.question1.name,
                "question": self.question1_loc_en.text,
                "answer": self.answer1_loc_en.text,
            },
        )

        self.assertDictEqual(
            results[1],
            {
                "name": "first_question",
                "question": "first_question",
                "answer": "first_answer",
            },
        )
