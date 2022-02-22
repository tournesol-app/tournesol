import React, { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { ChoicesFilterSection } from 'src/components';
import {
  availableRecommendationsLanguages,
  getLanguageName,
} from 'src/utils/constants';

interface Props {
  value: string;
  onChange: (value: string) => void;
}

function LanguageFilter(props: Props) {
  const { t } = useTranslation();

  const languageChoices: Record<string, string> = useMemo(
    () =>
      Object.fromEntries(
        availableRecommendationsLanguages.map((language) => [
          language,
          getLanguageName(t, language),
        ])
      ),
    [t]
  );

  return (
    <ChoicesFilterSection
      title={t('filter.language')}
      multipleChoice
      choices={languageChoices}
      {...props}
    ></ChoicesFilterSection>
  );
}

export default LanguageFilter;
