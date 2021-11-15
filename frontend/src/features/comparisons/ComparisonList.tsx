import React from 'react';
import { Link } from 'react-router-dom';

import { Grid, Container, makeStyles, Theme } from '@material-ui/core';

import type { Comparison } from 'src/services/openapi';
import VideoThumb from 'src/features/videos/VideoThumb';
import FromVideoId from 'src/features/videos/FromVideoId';

const useStyles = makeStyles((theme: Theme) => ({
  content: {
    padding: theme.spacing(3),
    maxWidth: 640,
  },
  comparisonContainer: {
    marginBottom: 8,
  },
  playerWrapper: {
    aspectRatio: '16 / 9',
  },
  centering: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
  },
}));

const VideoThumbFromVideoId = FromVideoId(VideoThumb);

const ComparisonThumbnail = ({ comparison }: { comparison: Comparison }) => {
  const classes = useStyles();
  const { video_a, video_b } = comparison;
  return (
    <Grid container className={classes.comparisonContainer}>
      <Grid item xs={5} className={classes.playerWrapper}>
        <VideoThumbFromVideoId videoId={video_a.video_id} />
      </Grid>
      <Grid item xs={2} className={classes.centering}>
        <Link
          to={`/comparison/?videoA=${video_a.video_id}&videoB=${video_b.video_id}`}
        >
          <span>VS.</span>
        </Link>
      </Grid>
      <Grid item xs={5} className={classes.playerWrapper}>
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
