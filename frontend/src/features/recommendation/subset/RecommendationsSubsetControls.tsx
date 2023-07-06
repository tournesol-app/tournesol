import React from 'react';
import { useTranslation } from 'react-i18next';

import { Button, Stack, useTheme } from '@mui/material';
import { RadioButtonUnchecked, CheckCircleOutline } from '@mui/icons-material';

interface RecommendationsSubsetProps {
  controlsColor?: string;
  selectedDate: string;
  dateControlChangeCallback: (value: string) => void;
}

const RecommendationsSubsetControls = ({
  controlsColor = '#fff',
  selectedDate,
  dateControlChangeCallback,
}: RecommendationsSubsetProps) => {
  const theme = useTheme();
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
    <Stack direction="row" justifyContent="center" spacing={2}>
      {dateControls.map((control, idx) => (
        <Button
          key={`${idx}_${control.value}`}
          variant="outlined"
          disableElevation
          sx={{
            color:
              selectedDate === control.value
                ? theme.palette.primary.main
                : controlsColor,
            borderColor:
              selectedDate === control.value
                ? theme.palette.primary.main
                : controlsColor,
            '&:hover': { color: theme.palette.primary.main },
          }}
          startIcon={
            selectedDate === control.value ? (
              <CheckCircleOutline />
            ) : (
              <RadioButtonUnchecked />
            )
          }
          data-reco-date={control.value}
          onClick={onDateControlClick}
        >
          {control.label}
        </Button>
      ))}
    </Stack>
  );
};

export default RecommendationsSubsetControls;
