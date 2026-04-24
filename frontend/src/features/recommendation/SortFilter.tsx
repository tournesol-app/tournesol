import React from 'react';
import { useTranslation } from 'react-i18next';
import { ChoicesFilterSection } from 'src/components';

interface Props {
  value: string;
  onChange: (value: string) => void;
}

function SortFilter(props: Props) {
  const { t } = useTranslation();

  const sortChoices = {
    top_rated: t('filter.topRated'),
    most_recent: t('filter.mostRecent'),
  };

  return (
    <ChoicesFilterSection
      title={t('filter.sortBy')}
      choices={sortChoices}
      radio
      {...props}
    />
  );
}

export default SortFilter;
