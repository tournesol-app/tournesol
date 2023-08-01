import React from 'react';
import { useTranslation } from 'react-i18next';
import { ChoicesFilterSection } from 'src/components';

interface Props {
  value: string;
  onChange: (value: string) => void;
}

function AdvancedFilter(props: Props) {
  const { t } = useTranslation();

  const choices = {
    unsafe: t('filter.includeAllVideos'),
    exclude_compared: t('filter.excludeComparedVideos'),
  };

  const tooltips = {
    unsafe: t('filter.unsafeTooltip'),
    exclude_compared: t('filter.excludeComparedTooltip'),
  };

  return (
    <ChoicesFilterSection
      title={t('filter.advanced')}
      multipleChoice
      choices={choices}
      tooltips={tooltips}
      {...props}
    ></ChoicesFilterSection>
  );
}

export default AdvancedFilter;
