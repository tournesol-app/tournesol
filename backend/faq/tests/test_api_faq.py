"""
All test cases of the `faq` views.
"""

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from faq.models import FAQAnswerLocale, FAQEntry, FAQuestionLocale


def create_entry(name, rank, enabled):
    return FAQEntry.objects.create(name=name, rank=rank, enabled=enabled)


def create_answer(question, lang, text=None):
    if not text:
        text = question.name

    return FAQAnswerLocale.objects.create(question=question, language=lang, text=text)


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

        self.question1 = create_entry("i_dont_understand_why", 20, True)

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

        self.answer1_loc_en = create_answer(
            self.question1, self.default_lang, "Tournesol aims to..."
        )
        self.answer1_loc_fr = create_answer(
            self.question1, self.available_lang, "Tournesol cherche à..."
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
        `en` translation must be returned.
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
        When the requested translation is not available in the database, the
        `en` translation must be returned.
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
        When a known language is requested, the matching translation must be
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
        self.question1.answers.all().delete()

        response = self.client.get(self.faq_base_url)
        results = response.data["results"]
        self.assertListEqual(results, [])

    def test_list_faq_disabled_questions_dont_appear(self):
        """
        Disabled questions must not be returned by the API.
        """
        question = create_entry("new_question", 1, True)
        create_answer(question, self.default_lang)

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
        question = create_entry("first_question", self.question1.rank - 1, True)
        create_answer(question, self.default_lang, "first_answer")

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
