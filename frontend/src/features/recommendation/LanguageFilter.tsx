import React from 'react';
import { useTranslation } from 'react-i18next';
import { ChoicesFilterSection } from 'src/components';

interface Props {
  value: string;
  onChange: (value: string) => void;
}

function LanguageFilter(props: Props) {
  const { t } = useTranslation();

  const languageChoices = {
    en: t('language.english'),
    fr: t('language.french'),
    de: t('language.german'),
  };

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
