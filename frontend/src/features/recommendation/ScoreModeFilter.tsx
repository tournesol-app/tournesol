import React from 'react';
import { useTranslation } from 'react-i18next';
import { ChoicesFilterSection } from 'src/components';

import { ScoreModeEnum } from 'src/features/recommendation/RecommendationApi';

interface Props {
  value: string;
  onChange: (value: string) => void;
}

function ScoreModeFilter(props: Props) {
  const { t } = useTranslation();

  const scoreModeChoices = {
    [ScoreModeEnum.DEFAULT]: t('filter.scoreMode.default'),
    [ScoreModeEnum.ALL_EQUAL]: t('filter.scoreMode.allEqual'),
    [ScoreModeEnum.TRUSTED_ONLY]: t('filter.scoreMode.trustedOnly'),
  };

  return (
    <ChoicesFilterSection
      title={t('filter.scoreModeSection')}
      choices={scoreModeChoices}
      radio
      {...props}
    />
  );
}

export default ScoreModeFilter;
