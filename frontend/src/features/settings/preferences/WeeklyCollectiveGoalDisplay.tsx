import React from 'react';
import { useTranslation } from 'react-i18next';

import {
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  SelectChangeEvent,
} from '@mui/material';

import {
  BlankEnum,
  ComparisonUi_weeklyCollectiveGoalDisplayEnum,
} from 'src/services/openapi';

interface WeeklyCollectiveGoalDisplayProps {
  compUiWeeklyColGoalDisplay:
    | ComparisonUi_weeklyCollectiveGoalDisplayEnum
    | BlankEnum;
  setCompUiWeeklyColGoalDisplay: (
    target: ComparisonUi_weeklyCollectiveGoalDisplayEnum | BlankEnum
  ) => void;
  pollName: string;
}

const WeeklyCollectiveGoalDisplay = ({
  setCompUiWeeklyColGoalDisplay,
  compUiWeeklyColGoalDisplay,
  pollName,
}: WeeklyCollectiveGoalDisplayProps) => {
  const { t } = useTranslation();

  const changeCompUiDisplayWeeklyColGoal = (event: SelectChangeEvent) => {
    setCompUiWeeklyColGoalDisplay(
      event.target.value as
        | ComparisonUi_weeklyCollectiveGoalDisplayEnum
        | BlankEnum
    );
  };

  const settingChoices = [
    {
      label: t('pollUserSettingsForm.always'),
      value: ComparisonUi_weeklyCollectiveGoalDisplayEnum.ALWAYS,
    },
    {
      label: t('pollUserSettingsForm.websiteOnly'),
      value: ComparisonUi_weeklyCollectiveGoalDisplayEnum.WEBSITE_ONLY,
    },
    {
      label: t('pollUserSettingsForm.embeddedOnly'),
      value: ComparisonUi_weeklyCollectiveGoalDisplayEnum.EMBEDDED_ONLY,
    },
    {
      label: t('pollUserSettingsForm.never'),
      value: ComparisonUi_weeklyCollectiveGoalDisplayEnum.NEVER,
    },
  ]

  return (
    <FormControl fullWidth>
      <InputLabel
        id="label__comparison_ui__weekly_collective_goal_display"
        color="secondary"
      >
        {t('pollUserSettingsForm.displayTheTheWeeklyCollectiveGoal')}
      </InputLabel>
      <Select
        size="small"
        color="secondary"
        id="comparison_ui__weekly_collective_goal_display"
        labelId="label__comparison_ui__weekly_collective_goal_display"
        value={compUiWeeklyColGoalDisplay}
        label={t('pollUserSettingsForm.displayTheTheWeeklyCollectiveGoal')}
        onChange={changeCompUiDisplayWeeklyColGoal}
        inputProps={{
          'data-testid': `${pollName}_weekly_collective_goal_display`,
        }}
      >
        {settingChoices.map((item) => (
          <MenuItem key={item.value} value={item.value}>
            {item.label}
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
};

export default WeeklyCollectiveGoalDisplay;
