import React from 'react';
import { useTranslation } from 'react-i18next';
import { Grid, Container, Theme, Tooltip, Fab, Box } from '@mui/material';
import makeStyles from '@mui/styles/makeStyles';
import { Compare as CompareIcon } from '@mui/icons-material';

import type { Comparison } from 'src/services/openapi';
import VideoCard from '../videos/VideoCard';

const useStyles = makeStyles((theme: Theme) => ({
  content: {
    padding: theme.spacing(3),
    [theme.breakpoints.down('sm')]: {
      padding: theme.spacing(0),
    },
    maxWidth: 840,
  },
  comparisonContainer: {
    marginBottom: 16,
    display: 'flex',
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'stretch',
    gap: '16px',
  },
  centering: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
  },
}));

const ComparisonThumbnail = ({ comparison }: { comparison: Comparison }) => {
  const { t } = useTranslation();
  const classes = useStyles();
  const { entity_a, entity_b } = comparison;
  return (
    <Box className={classes.comparisonContainer}>
      <VideoCard compact video={entity_a} />
      <Box className={classes.centering} style={{ position: 'relative' }}>
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
            style={{ backgroundColor: '#F1EFE7' }}
            size="small"
          >
            <CompareIcon style={{ color: '#B6B1A1' }} />
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
  const classes = useStyles();

  return (
    <Container className={classes.content}>
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
