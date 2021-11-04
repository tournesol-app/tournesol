import React from 'react';

import { Typography, makeStyles, Grid, IconButton } from '@material-ui/core';
import { Add as AddIcon } from '@material-ui/icons';
import type {
  PaginatedVideoSerializerWithCriteriaList,
  VideoSerializerWithCriteria,
} from 'src/services/openapi';
import VideoCard from '../videos/VideoCard';
import { CompareNowAction } from 'src/utils/action';
import { addToRateLaterList } from '../rateLater/rateLaterAPI';
import { useAppSelector } from 'src/app/hooks';
import { selectLogin } from 'src/features/login/loginSlice';

const useStyles = makeStyles(() => ({
  card: {
    alignItems: 'center',
  },
}));

function VideoList({
  videos,
}: {
  videos: PaginatedVideoSerializerWithCriteriaList;
}) {
  const classes = useStyles();

  const loginState = useAppSelector(selectLogin);

  const AddToRateLaterList = ({ videoId }: { videoId: string }) => {
    const video_id = videoId;
    return (
      <div>
        {loginState.access_token && (
          <IconButton
            size="medium"
            color="secondary"
            onClick={async () => {
              await addToRateLaterList(loginState, { video_id });
            }}
          >
            <AddIcon />
          </IconButton>
        )}
      </div>
    );
  };

  return (
    <div>
      {videos.results?.length ? (
        videos.results.map((video: VideoSerializerWithCriteria) => (
          <Grid container className={classes.card} key={video.video_id}>
            <Grid item xs={12}>
              <VideoCard
                video={video}
                actions={[CompareNowAction, AddToRateLaterList]}
              />
            </Grid>
          </Grid>
        ))
      ) : (
        <Typography variant="h5" component="h2">
          No video corresponds to your research criterias
        </Typography>
      )}
    </div>
  );
}

export default VideoList;
