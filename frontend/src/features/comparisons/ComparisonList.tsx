import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Grid, Container, Tooltip, Fab, Box, useTheme } from '@mui/material';
import { Compare as CompareIcon } from '@mui/icons-material';

import type { Comparison } from 'src/services/openapi';
import EntityCard from 'src/components/entity/EntityCard';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';

const ComparisonThumbnail = ({ comparison }: { comparison: Comparison }) => {
  const { t } = useTranslation();
  const { baseUrl } = useCurrentPoll();
  const { entity_a, entity_b } = comparison;

  return (
    <Box
      sx={{
        marginBottom: '16px',
        display: 'flex',
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'stretch',
        gap: '16px',
      }}
    >
      <EntityCard
        compact
        entity={entity_a}
        entityTypeConfig={{ video: { displayPlayer: false } }}
      />
      <Box
        sx={{
          position: 'relative',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
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
            to={`${baseUrl}/comparison/?uidA=${entity_a.uid}&uidB=${entity_b.uid}`}
            sx={{ backgroundColor: '#F1EFE7' }}
            size="small"
          >
            <CompareIcon sx={{ color: '#B6B1A1' }} />
          </Fab>
        </Tooltip>
      </Box>
      <EntityCard
        compact
        entity={entity_b}
        entityTypeConfig={{ video: { displayPlayer: false } }}
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
