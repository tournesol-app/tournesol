import React from 'react';
import { useTranslation } from 'react-i18next';
import { Grid, Container, Tooltip, Fab, Box, useTheme } from '@mui/material';
import { Compare as CompareIcon } from '@mui/icons-material';

import type { Comparison } from 'src/services/openapi';
import VideoCard from '../videos/VideoCard';

const ComparisonThumbnail = ({ comparison }: { comparison: Comparison }) => {
  const { t } = useTranslation();
  const { entity_a, entity_b } = comparison;
  return (
    <Box
      sx={{
        marginBottom: 16,
        display: 'flex',
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'stretch',
        gap: '16px',
      }}
    >
      <VideoCard compact video={entity_a} />
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
            component="a"
            href={`/comparison/?videoA=${entity_a.video_id}&videoB=${entity_b.video_id}`}
            sx={{ backgroundColor: '#F1EFE7' }}
            size="small"
          >
            <CompareIcon sx={{ color: '#B6B1A1' }} />
          </Fab>
        </Tooltip>
      </Box>
      <VideoCard compact video={entity_b} />
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
                key={`${c.entity_a.video_id}${c.entity_b.video_id}`}
                comparison={c}
              />
            ))}
        </Grid>
      </Grid>
    </Container>
  );
};

export default Comparisons;
