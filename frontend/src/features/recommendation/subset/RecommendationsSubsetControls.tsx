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
    <Stack
      direction="row"
      spacing={2}
      sx={{
        justifyContent: 'center',
      }}
    >
      {dateControls.map((control, idx) => (
        <Button
          key={`${idx}_${control.value}`}
          variant="outlined"
          disableElevation
          sx={[
            {
              '&:hover': {
                color: theme.palette.primary.main,
                borderColor: theme.palette.primary.main,
              },
            },
            selectedDate === control.value
              ? {
                  color: theme.palette.primary.main,
                  borderColor: theme.palette.primary.main,
                }
              : {
                  color: controlsColor,
                  borderColor: controlsColor,
                },
          ]}
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
