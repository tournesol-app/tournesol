import React from 'react';

import {
  Grid,
  Container,
  makeStyles,
  Theme,
  Tooltip,
  Fab,
} from '@material-ui/core';
import { Compare as CompareIcon } from '@material-ui/icons';
import type { Comparison } from 'src/services/openapi';
import VideoThumb from 'src/features/videos/VideoThumb';
import { useVideoMetadata } from 'src/features/videos/VideoApi';

const useStyles = makeStyles((theme: Theme) => ({
  content: {
    padding: theme.spacing(3),
    maxWidth: 840,
  },
  comparisonContainer: {
    marginBottom: 16,
    display: 'flex',
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'stretch',
  },
  playerWrapper: {
    aspectRatio: '16 / 9',
    width: 'calc(50% - 26px)',
  },
  centering: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
  },
}));

const VideoThumbFromVideoId = ({ videoId }: { videoId: string }) => {
  const video = useVideoMetadata(videoId);
  return <VideoThumb video={video} />;
};

const ComparisonThumbnail = ({ comparison }: { comparison: Comparison }) => {
  const classes = useStyles();
  const { video_a, video_b } = comparison;
  return (
    <Grid container className={classes.comparisonContainer}>
      <Grid item className={classes.playerWrapper}>
        <VideoThumbFromVideoId videoId={video_a.video_id} />
      </Grid>
      <Grid item className={classes.centering} style={{ position: 'relative' }}>
        <div
          style={{
            border: '1px solid #F1EFE7',
            position: 'absolute',
            height: 'calc(100% - 32px)',
            width: 0,
          }}
        />
        <Tooltip title="Compare now" placement="top">
          <Fab
            component="a"
            href={`/comparison/?videoA=${video_a.video_id}&videoB=${video_b.video_id}`}
            style={{ backgroundColor: '#F1EFE7' }}
            size="small"
          >
            <CompareIcon style={{ color: '#B6B1A1' }} />
          </Fab>
        </Tooltip>
      </Grid>
      <Grid item className={classes.playerWrapper}>
        <VideoThumbFromVideoId videoId={video_b.video_id} />
      </Grid>
    </Grid>
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
                key={`${c.video_a.video_id}${c.video_b.video_id}`}
                comparison={c}
              />
            ))}
        </Grid>
      </Grid>
    </Container>
  );
};

export default Comparisons;
