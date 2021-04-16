from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from backend.api_v2.helpers import WithPKOverflowProtection
from backend.constants import fields, comments


class FeatureSerializer(serializers.Serializer):
    """Serialize features used to rate videos."""
    feature = serializers.CharField(required=True, help_text="Feature short name")
    description = serializers.CharField(required=True, help_text="Feature full description")
    color = serializers.CharField(required=True, help_text="Color of the feature")
    enabled_by_default = serializers.BooleanField(required=True,
                                                  help_text="Is enabled for new users?")


class ReportFieldSerializer(serializers.Serializer):
    """Video reporting fields."""
    field = serializers.CharField(required=True, help_text="Short field name")
    description = serializers.CharField(required=True, help_text="Field full description")


class ConstantsSerializerV2(serializers.Serializer):
    """Serialize statistics for the website."""
    features = FeatureSerializer(many=True, help_text="Features used on the website to rate videos")
    report_fields = ReportFieldSerializer(many=True, help_text="Video reporting fields")
    search_divider_coefficient = serializers.FloatField(required=True,
                                                        help_text=comments['SEARCH_DIVIDER_COEFF'])
    search_feature_constant_add = serializers.FloatField(
        required=True, help_text=comments['SEARCH_FEATURE_CONST_ADD'])
    recaptcha_v2_public_key = serializers.CharField(required=True,
                                                    help_text=comments['DRF_RECAPTCHA_PUBLIC_KEY'])
    youtubeVideoIdRegexSymbol = serializers.CharField(
        required=True, help_text=comments['youtubeVideoIdRegexSymbol'])
    minNumRateLater = serializers.IntegerField(
        required=True, help_text=comments['minNumRateLater']
    )


class ConstantsViewSetV2(viewsets.ViewSet, WithPKOverflowProtection):
    """Get constants."""
    serializer_class = ConstantsSerializerV2
    permission_classes = [AllowAny]

    # need a list, otherwise router will not register this viewset
    @extend_schema(exclude=True, responses={
                200: ConstantsSerializerV2(
                    many=True),
                400: None})
    def list(self, request):
        return Response({})

    @extend_schema(
        responses={
            200: ConstantsSerializerV2(
                many=False)},
        operation_id="view_constants")
    @action(methods=['GET'], detail=False)
    def view_constants(self, request):
        """Get constants."""

        features = []
        assert len(fields['featureNames']) == len(fields['featureColors'])
        assert set(fields['featureNames'].keys()) == set(fields['featureColors'].keys())
        for key in fields['featureNames'].keys():
            features.append({
                'feature': key,
                'description': fields['featureNames'][key],
                'color': fields['featureColors'][key],
                'enabled_by_default': fields['featureIsEnabledByDeFault'][key],
            })

        report_fields = []
        for key, val in fields['videoReportFieldNames'].items():
            report_fields.append({
                'field': key,
                'description': val,
            })

        data = {
            'recaptcha_v2_public_key': fields['DRF_RECAPTCHA_PUBLIC_KEY'],
            'search_feature_constant_add': fields['SEARCH_FEATURE_CONST_ADD'],
            'search_divider_coefficient': fields['SEARCH_DIVIDER_COEFF'],
            'report_fields': report_fields,
            'features': features,
            'youtubeVideoIdRegexSymbol': fields['youtubeVideoIdRegexSymbol'],
            'minNumRateLater': fields['minNumRateLater'],
        }

        return Response(ConstantsSerializerV2(data, many=False).data)
