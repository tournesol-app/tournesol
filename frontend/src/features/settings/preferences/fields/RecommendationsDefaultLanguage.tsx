import React from 'react';
import { useTranslation } from 'react-i18next';

import { LanguageField } from 'src/features/recommendation/LanguageFilter';

interface RecommendationsDefaultLanguageProps {
  value: string[];
  onChange: (target: string[]) => void;
}

const RecommendationsDefaultLanguage = ({
  value,
  onChange,
}: RecommendationsDefaultLanguageProps) => {
  const { t } = useTranslation();

  return (
    <LanguageField
      label={t('pollUserSettingsForm.recommendations.defaultLanguages')}
      helperText={t(
        'pollUserSettingsForm.recommendations.keepEmptyToSelectAllLang'
      )}
      value={value.join(',')}
      onChange={(target) => {
        onChange(target.split(','));
      }}
    />
  );
};

export default RecommendationsDefaultLanguage;
