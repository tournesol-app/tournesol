import React from 'react';

import {
  Box,
  IconButton,
  Paper,
  Typography,
  useMediaQuery,
  useTheme,
} from '@mui/material';
import {
  KeyboardArrowLeft,
  KeyboardArrowRight,
  KeyboardDoubleArrowLeft,
  KeyboardDoubleArrowRight,
} from '@mui/icons-material';

import { CriteriaIcon } from 'src/components';
import { CriteriaLabel } from 'src/features/comparisons/CriteriaSlider';

export const BUTTON_SCORE_MAX = 2;
const BUTTON_SCORE_STEP = 1;

interface ScoreButtonProps {
  children: React.ReactNode;
  score: number;
  selected: boolean;
  disabled: boolean;
  onClick: (score: number) => Promise<void>;
}

interface CriterionButtonsProps {
  critName: string;
  critLabel: string;
  givenScore?: number;
  disabled: boolean;
  onClick: (score: number) => Promise<void>;
}

export const scoreButtons = [
  {
    score: -BUTTON_SCORE_MAX,
    icons: <KeyboardDoubleArrowLeft />,
  },
  {
    score: -BUTTON_SCORE_STEP,
    icons: <KeyboardArrowLeft />,
  },
  {
    score: 0,
    icons: '=',
  },
  {
    score: BUTTON_SCORE_STEP,
    icons: <KeyboardArrowRight />,
  },
  {
    score: BUTTON_SCORE_MAX,
    icons: <KeyboardDoubleArrowRight />,
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
  const hover = useMediaQuery('(pointer:fine) and (hover:hover)');

  return (
    <IconButton
      disabled={disabled}
      color="secondary"
      onClick={() => onClick(score)}
      data-criterion-input-type="score-button"
      data-criterion-input-score={score}
      data-criterion-input-selected={selected}
      sx={{
        minWidth: '40px',
        borderRadius: '4px',
        backgroundColor: selected
          ? theme.palette.primary.main
          : theme.palette.background.mobileButton,
        color: selected ? 'text.primary' : undefined,
        '&:hover': hover
          ? {
              color: 'white',
              backgroundColor: selected
                ? theme.palette.secondary.dark
                : theme.palette.secondary.main,
            }
          : {
              color: undefined,
              backgroundColor: selected
                ? theme.palette.primary.main
                : theme.palette.background.mobileButton,
            },
      }}
    >
      {children}
    </IconButton>
  );
};

const CriterionButtons = React.forwardRef(function (
  { critName, critLabel, givenScore, disabled, onClick }: CriterionButtonsProps,
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
        <Box
          width="100%"
          display="flex"
          sx={{ justifyContent: { xs: 'space-between', md: 'space-around' } }}
        >
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

CriterionButtons.displayName = 'CriterionButtons';

export default CriterionButtons;
