import React, { useCallback, useMemo } from 'react';
import FormGroup from '@mui/material/FormGroup';
import FormControlLabel from '@mui/material/FormControlLabel';
import Tooltip from '@mui/material/Tooltip';
import Checkbox from '@mui/material/Checkbox';
import usePersonalCriteriaScores from 'src/hooks/usePersonalCriteriaScores';
import { useTranslation } from 'react-i18next';

const PersonalScoreCheckbox = () => {
  const { t } = useTranslation();
  const {
    canActivatePersonalScores,
    reasonWhyPersonalScoresCannotBeActivated,
    personalScoresActivated,
    setPersonalScoresActivated,
  } = usePersonalCriteriaScores();

  const handleChange = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      setPersonalScoresActivated(event.target.checked);
    },
    [setPersonalScoresActivated]
  );

  const tooltip = useMemo(() => {
    switch (reasonWhyPersonalScoresCannotBeActivated) {
      case 'notLoggedIn':
        return t(
          'personalCriteriaScores.reasonWhyItCannotBeActivated.notLoggedIn'
        );
      case 'noPersonalScore':
        return t(
          'personalCriteriaScores.reasonWhyItCannotBeActivated.noPersonalScore'
        );
    }
  }, [reasonWhyPersonalScoresCannotBeActivated, t]);

  return (
    <Tooltip title={tooltip || ''} placement="top-start">
      <FormGroup>
        <FormControlLabel
          control={
            <Checkbox
              checked={personalScoresActivated}
              onChange={handleChange}
              disabled={!canActivatePersonalScores}
            />
          }
          label={t<string>('personalCriteriaScores.activatePersonalScores')}
        />
      </FormGroup>
    </Tooltip>
  );
};

export default PersonalScoreCheckbox;
