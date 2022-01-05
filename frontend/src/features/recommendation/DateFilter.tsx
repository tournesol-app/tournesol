import React from 'react';
import { useTranslation } from 'react-i18next';
import { ChoicesFilterSection } from 'src/components';

interface Props {
  value: string;
  onChange: (value: string) => void;
}

function DateFilter(props: Props) {
  const { t } = useTranslation();

  const dateChoices = {
    Today: t('filter.today'),
    Week: t('filter.thisWeek'),
    Month: t('filter.thisMonth'),
    Year: t('filter.thisYear'),
  };

  return (
    <ChoicesFilterSection
      title={t('filter.uploadDate')}
      choices={dateChoices}
      {...props}
    />
  );
}

export default DateFilter;
