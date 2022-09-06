"""
Administration interface of the `faq` app.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from faq.models import FAQAnswer, FAQAnswerLocale, FAQuestion, FAQuestionLocale


class HasAnswerListFilter(admin.SimpleListFilter):
    title = _("has answer?")
    parameter_name = "has_answer"

    def lookups(self, request, model_admin):
        return (
            (1, _("Yes")),
            (0, _("No")),
        )

    def queryset(self, request, queryset):
        if self.value() == "1":
            return queryset.filter(
                answer__isnull=False,
            )
        if self.value() == "0":
            return queryset.filter(
                answer__isnull=True,
            )
        return queryset


class FAQuestionLocaleInline(admin.TabularInline):
    model = FAQuestionLocale
    extra = 0


class FAQAnswerLocaleInline(admin.TabularInline):
    model = FAQAnswerLocale
    extra = 0


@admin.register(FAQuestion)
class FAQuestionAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("name", "rank", "enabled", "has_answer")
    list_filter = (HasAnswerListFilter, "enabled")
    ordering = ("rank",)
    inlines = (FAQuestionLocaleInline,)

    def get_queryset(self, request):
        qst = super().get_queryset(request)
        qst = qst.select_related("answer")
        return qst

    @admin.display(description="has answer?", boolean=True)
    def has_answer(self, obj) -> bool:
        try:
            obj.answer.pk
        except FAQuestion.answer.RelatedObjectDoesNotExist:
            return False
        else:
            return True


@admin.register(FAQAnswer)
class FAQAnswerAdmin(admin.ModelAdmin):
    search_fields = ("name", "question__name")
    list_display = (
        "name",
        "question",
        "get_q_rank",
        "get_q_enabled",
    )
    list_filter = ("question__enabled",)
    inlines = (FAQAnswerLocaleInline,)

    def get_queryset(self, request):
        qst = super().get_queryset(request)
        qst = qst.select_related("question").order_by("question__rank")
        return qst

    @admin.display(description="question rank", ordering="question__rank")
    def get_q_rank(self, obj):
        return obj.question.rank

    @admin.display(
        description="question enabled?", ordering="question__enabled", boolean=True
    )
    def get_q_enabled(self, obj):
        return obj.question.enabled
