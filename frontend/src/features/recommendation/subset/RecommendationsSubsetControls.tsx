import React from 'react';
import { useTranslation } from 'react-i18next';

import { Stack, ToggleButton, ToggleButtonGroup } from '@mui/material';

interface RecommendationsSubsetProps {
  selectedDate: string;
  dateControlChangeCallback: (value: string) => void;
}

const RecommendationsSubsetControls = ({
  selectedDate,
  dateControlChangeCallback,
}: RecommendationsSubsetProps) => {
  const { t } = useTranslation();

  const onDateControlClick = (event: React.MouseEvent<HTMLElement>) => {
    dateControlChangeCallback(
      event.currentTarget.getAttribute('data-reco-date') ?? ''
    );
  };

  const dateControls = [
    {
      value: 'Month',
      label: t('recommendationsSubsetControls.bestOfLastMonth'),
    },
    {
      value: '',
      label: t('recommendationsSubsetControls.bestOfAllTime'),
    },
  ];

  return (
    <Stack direction="row" spacing={2}>
      <ToggleButtonGroup
        size="small"
        exclusive
        value={selectedDate}
        fullWidth
        sx={{ backgroundColor: (theme) => theme.palette.background.primary }}
        color="secondary"
      >
        {dateControls.map((control, idx) => (
          <ToggleButton
            value={control.value}
            key={`${idx}_${control.value}`}
            sx={{ fontWeight: 'bold' }}
            data-reco-date={control.value}
            onClick={onDateControlClick}
          >
            {control.label}
          </ToggleButton>
        ))}
      </ToggleButtonGroup>
    </Stack>
  );
};

export default RecommendationsSubsetControls;
