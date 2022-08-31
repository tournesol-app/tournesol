"""
Administration interface of the `faq` app.
"""

from django.contrib import admin

from faq.models import FAQAnswer, FAQAnswerLocale, FAQuestion, FAQuestionLocale


class FAQuestionLocaleInline(admin.TabularInline):
    model = FAQuestionLocale
    extra = 0


class FAQAnswerLocaleInline(admin.TabularInline):
    model = FAQAnswerLocale
    extra = 0


@admin.register(FAQuestion)
class FAQuestionAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("name", "rank")
    inlines = (FAQuestionLocaleInline,)


@admin.register(FAQAnswer)
class FAQAnswerAdmin(admin.ModelAdmin):
    search_fields = (
        "name",
        "question__name",
    )
    list_display = (
        "name",
        "question",
        "get_q_rank",
    )
    inlines = (FAQAnswerLocaleInline,)

    def get_queryset(self, request):
        qst = super().get_queryset(request)
        qst = qst.select_related("question").order_by("question__rank")
        return qst

    @admin.display(description="question rank", ordering="question__rank")
    def get_q_rank(self, obj):
        return obj.question.rank
