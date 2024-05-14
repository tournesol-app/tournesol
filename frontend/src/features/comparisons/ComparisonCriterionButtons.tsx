import React from 'react';

import { Box, IconButton, Paper, Typography, useTheme } from '@mui/material';
import { Add, Balance } from '@mui/icons-material';

import { CriteriaIcon } from 'src/components';
import { CriteriaLabel } from './CriteriaSlider';

export const BUTTON_SCORE_MAX = 2;
const BUTTON_SCORE_STEP = 1;

interface ScoreButtonProps {
  children: React.ReactNode;
  score: number;
  selected: boolean;
  disabled: boolean;
  onClick: (score: number) => Promise<void>;
}

interface ComparisonCriterionButtonsProps {
  critName: string;
  critLabel: string;
  givenScore?: number;
  disabled: boolean;
  onClick: (score: number) => Promise<void>;
}

export const scoreButtons = [
  {
    score: -BUTTON_SCORE_MAX,
    icons: (
      <>
        <Add />
        <Add />
      </>
    ),
  },
  {
    score: -BUTTON_SCORE_STEP,
    icons: <Add />,
  },
  {
    score: 0,
    icons: <Balance />,
  },
  {
    score: BUTTON_SCORE_STEP,
    icons: <Add />,
  },
  {
    score: BUTTON_SCORE_MAX,
    icons: (
      <>
        <Add />
        <Add />
      </>
    ),
  },
];

const ScoreButton = ({
  children,
  score,
  selected,
  disabled,
  onClick,
}: ScoreButtonProps) => {
  const theme = useTheme();

  return (
    <IconButton
      disabled={disabled}
      color="secondary"
      aria-label="todo"
      onClick={() => onClick(score)}
      sx={{
        borderRadius: '4px',
        backgroundColor: selected ? theme.palette.primary.main : 'grey.200',
        color: selected ? 'white' : undefined,
        '&:hover': {
          color: 'white',
          backgroundColor: selected
            ? theme.palette.secondary.dark
            : theme.palette.secondary.main,
        },
      }}
    >
      {children}
    </IconButton>
  );
};

const ComparisonCriterionButtons = React.forwardRef(function (
  {
    critName,
    critLabel,
    givenScore,
    disabled,
    onClick,
  }: ComparisonCriterionButtonsProps,
  ref
) {
  return (
    <Box ref={ref}>
      <Paper sx={{ py: 2, px: 1 }}>
        <Box display="flex" justifyContent="center" mb={2}>
          <CriteriaIcon criteriaName={critName} sx={{ mr: 1 }} />
          <Typography fontSize={{ xs: '90%', sm: '100%' }}>
            <CriteriaLabel criteria={critName} criteriaLabel={critLabel} />
          </Typography>
        </Box>
        <Box display="flex" justifyContent="space-between" width="100%">
          {scoreButtons.map((btn, idx) => (
            <ScoreButton
              key={`criterion_button_${idx}`}
              score={btn.score}
              selected={btn.score === givenScore}
              disabled={disabled}
              onClick={onClick}
            >
              {btn.icons}
            </ScoreButton>
          ))}
        </Box>
      </Paper>
    </Box>
  );
});

ComparisonCriterionButtons.displayName = 'CriterionComparisonButtons';

export default ComparisonCriterionButtons;
