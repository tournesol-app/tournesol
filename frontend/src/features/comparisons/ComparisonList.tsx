import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import { Grid, Container, Tooltip, Fab, Box, useTheme } from '@mui/material';
import { Compare as CompareIcon, Smartphone } from '@mui/icons-material';

import type { Comparison } from 'src/services/openapi';
import EntityCard from 'src/components/entity/EntityCard';
import { BUTTON_SCORE_MAX } from 'src/features/comparisons/inputs/CriterionButtons';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import { getCriterionScoreMax } from 'src/utils/criteria';

const ComparisonThumbnail = ({ comparison }: { comparison: Comparison }) => {
  const { t } = useTranslation();
  const { baseUrl, options } = useCurrentPoll();
  const { entity_a, entity_b } = comparison;

  const mainScoreMax = getCriterionScoreMax(
    comparison?.criteria_scores,
    options?.mainCriterionName
  );

  const buttonsUsed = mainScoreMax == BUTTON_SCORE_MAX;

  return (
    <Box
      sx={{
        mb: 2,
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'stretch',
        gap: 1,
      }}
    >
      <EntityCard
        compact
        result={{
          entity: entity_a,
          entity_contexts: comparison.entity_a_contexts,
        }}
        entityTypeConfig={{ video: { displayPlayer: false } }}
        displayContextAlert={true}
      />
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          position: 'relative',
        }}
      >
        <div
          style={{
            border: '1px solid #F1EFE7',
            position: 'absolute',
            height: 'calc(100% - 32px)',
            width: 0,
          }}
        />
        <Tooltip title={`${t('comparisons.goToComparison')}`} placement="top">
          <Fab
            component={Link}
            to={`${baseUrl}/comparison?uidA=${entity_a.uid}&uidB=${entity_b.uid}`}
            sx={{ backgroundColor: '#F1EFE7' }}
            size="small"
          >
            {buttonsUsed ? (
              <Smartphone sx={{ color: 'neutral.main' }} />
            ) : (
              <CompareIcon sx={{ color: 'neutral.main' }} />
            )}
          </Fab>
        </Tooltip>
      </Box>
      <EntityCard
        compact
        result={{
          entity: entity_b,
          entity_contexts: comparison.entity_b_contexts,
        }}
        entityTypeConfig={{ video: { displayPlayer: false } }}
        displayContextAlert={true}
      />
    </Box>
  );
};

const Comparisons = ({
  comparisons,
}: {
  comparisons: Comparison[] | undefined;
}) => {
  const theme = useTheme();

  return (
    <Container
      sx={{
        padding: theme.spacing(3),
        [theme.breakpoints.down('sm')]: {
          padding: theme.spacing(0),
        },
        maxWidth: '840px !important',
      }}
    >
      <Grid container>
        <Grid item xs={12}>
          {comparisons &&
            comparisons.map((c) => (
              <ComparisonThumbnail
                key={`${c.entity_a.uid}${c.entity_b.uid}`}
                comparison={c}
              />
            ))}
        </Grid>
      </Grid>
    </Container>
  );
};

export default Comparisons;
