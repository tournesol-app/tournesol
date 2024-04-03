import React from 'react';

import { Box, IconButton, Paper, Typography } from '@mui/material';
import { Add, Balance } from '@mui/icons-material';

import { CriteriaIcon } from 'src/components';
import { CriteriaLabel } from './CriteriaSlider';

interface CriterionComparisonButtonsProps {
  critName: string;
  critLabel: string;
  onClick: (criteron: string, score: number) => Promise<void>;
}

const ComparisonCriterionButtons = React.forwardRef(function (
  { critName, critLabel, onClick }: CriterionComparisonButtonsProps,
  ref
) {
  return (
    <Box ref={ref}>
      <Paper sx={{ py: 2 }}>
        <Box display="flex" justifyContent="center" mb={1}>
          <CriteriaIcon criteriaName={critName} sx={{ mr: 1 }} />
          <Typography fontSize={{ xs: '90%', sm: '100%' }}>
            <CriteriaLabel criteria={critName} criteriaLabel={critLabel} />
          </Typography>
        </Box>
        <Box display="flex" justifyContent="space-between" width="100%">
          <IconButton
            color="secondary"
            aria-label="todo"
            onClick={() => onClick(critName, -2)}
          >
            <Add />
            <Add />
          </IconButton>
          <IconButton
            color="secondary"
            aria-label="todo"
            onClick={() => onClick(critName, -1)}
          >
            <Add />
          </IconButton>
          <IconButton
            color="secondary"
            aria-label="todo"
            onClick={() => onClick(critName, 0)}
          >
            <Balance />
          </IconButton>
          <IconButton
            color="secondary"
            aria-label="todo"
            onClick={() => onClick(critName, 1)}
          >
            <Add />
          </IconButton>
          <IconButton
            color="secondary"
            aria-label="todo"
            onClick={() => onClick(critName, 2)}
          >
            <Add />
            <Add />
          </IconButton>
        </Box>
      </Paper>
    </Box>
  );
});

ComparisonCriterionButtons.displayName = 'CriterionComparisonButtons';

export default ComparisonCriterionButtons;
