import React from 'react';
import { useTranslation } from 'react-i18next';
import { Grid, Container, Tooltip, Fab, Box, useTheme } from '@mui/material';
import { Compare as CompareIcon } from '@mui/icons-material';

import type { Comparison } from 'src/services/openapi';
import VideoCard from '../videos/VideoCard';
import { VideoObject } from 'src/utils/types';
import { videoFromRelatedEntity } from 'src/utils/entity';

const ComparisonThumbnail = ({ comparison }: { comparison: Comparison }) => {
  const { t } = useTranslation();
  const { entity_a, entity_b } = comparison;

  const videoA: VideoObject = videoFromRelatedEntity(entity_a);
  const videoB: VideoObject = videoFromRelatedEntity(entity_b);

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
      <VideoCard compact video={videoA} />
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
            href={`/comparison/?uidA=${entity_a.uid}&uidB=${entity_b.uid}`}
            sx={{ backgroundColor: '#F1EFE7' }}
            size="small"
          >
            <CompareIcon sx={{ color: '#B6B1A1' }} />
          </Fab>
        </Tooltip>
      </Box>
      <VideoCard compact video={videoB} />
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
                key={`${c.entity_a.metadata.video_id}${c.entity_b.metadata.video_id}`}
                comparison={c}
              />
            ))}
        </Grid>
      </Grid>
    </Container>
  );
};

export default Comparisons;
