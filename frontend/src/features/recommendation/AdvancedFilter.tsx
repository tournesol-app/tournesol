import React from 'react';
import { useTranslation } from 'react-i18next';
import { ChoicesFilterSection } from 'src/components';
import { useLoginState } from 'src/hooks';

interface Props {
  value: string;
  onChange: (value: string) => void;
}

function AdvancedFilter(props: Props) {
  const { t } = useTranslation();
  const { isLoggedIn } = useLoginState();

  const choices: { unsafe: string; exclude_compared?: string } = {
    unsafe: t('filter.includeAllVideos'),
    exclude_compared: t('filter.excludeComparedVideos'),
  };

  const tooltips: { unsafe: string; exclude_compared?: string } = {
    unsafe: t('filter.unsafeTooltip'),
    exclude_compared: t('filter.excludeComparedTooltip'),
  };

  if (!isLoggedIn) {
    delete choices['exclude_compared'];
    delete tooltips['exclude_compared'];
  }

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
