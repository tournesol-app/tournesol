import React from 'react';

import { Box, IconButton, Paper, Typography, useTheme } from '@mui/material';
import { Add, Balance } from '@mui/icons-material';

import { CriteriaIcon } from 'src/components';
import { CriteriaLabel } from './CriteriaSlider';

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
        backgroundColor: selected ? theme.palette.secondary.main : undefined,
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
  const scoreButtons = [
    {
      score: -2,
      icons: (
        <>
          <Add />
          <Add />
        </>
      ),
    },
    {
      score: -1,
      icons: <Add />,
    },
    {
      score: 0,
      icons: <Balance />,
    },
    {
      score: 1,
      icons: <Add />,
    },
    {
      score: 2,
      icons: (
        <>
          <Add />
          <Add />
        </>
      ),
    },
  ];

  return (
    <Box ref={ref}>
      <Paper sx={{ p: 2 }}>
        <Box display="flex" justifyContent="center" mb={1}>
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
