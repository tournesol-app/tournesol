import React from 'react';
import { useTranslation } from 'react-i18next';
import { ChoicesFilterSection } from 'src/components';

export const isPublicChoices = {
  true: 'Public',
  false: 'Private',
};

interface FilterProps {
  value: string;
  onChange: (value: string) => void;
}

function IsPublicFilter(props: FilterProps) {
  const { t } = useTranslation();

  const isPublicChoices = {
    true: t('public'),
    false: t('private'),
  };

  return (
    <ChoicesFilterSection
      title={t('filter.filterByVisibility')}
      choices={isPublicChoices}
      {...props}
    ></ChoicesFilterSection>
  );
}

export default IsPublicFilter;
