import React from 'react';
import { useTranslation } from 'react-i18next';

import { FormControlLabel, Switch } from '@mui/material';

interface ExtRecommendationSearchProps {
  value: boolean;
  onChange: (target: boolean) => void;
  pollName: string;
}

const ExtSearchRecommendation = ({
  value,
  onChange,
  pollName,
}: ExtRecommendationSearchProps) => {
  const { t } = useTranslation();

  return (
    <FormControlLabel
      control={
        <Switch
          name={`${pollName}_extension__search_reco`}
          checked={value}
          onChange={() => onChange(!value)}
          size="medium"
          color="secondary"
          inputProps={
            {
              'data-testid': `${pollName}_extension__search_reco`,
            } as React.InputHTMLAttributes<HTMLInputElement>
          }
        />
      }
      label={t('pollUserSettingsForm.includeTournesolResultsInYouTubeSearch')}
    />
  );
};

export default ExtSearchRecommendation;
