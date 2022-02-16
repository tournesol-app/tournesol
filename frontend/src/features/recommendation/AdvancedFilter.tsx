import React from 'react';
import { useTranslation } from 'react-i18next';
import { ChoicesFilterSection } from 'src/components';

interface Props {
  value: string;
  onChange: (value: string) => void;
}

function AdvancedFilter(props: Props) {
  const { t } = useTranslation();

  const safeChoice = {
    true: t('filter.includeAllVideos'),
  };

  return (
    <ChoicesFilterSection
      title={t('filter.advanced')}
      multipleChoice
      choices={safeChoice}
      tooltip={t('filter.unsafeTooltip')}
      {...props}
    ></ChoicesFilterSection>
  );
}

export default AdvancedFilter;
