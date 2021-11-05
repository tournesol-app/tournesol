import React from 'react';

import { Typography, makeStyles, Grid, IconButton } from '@material-ui/core';
import { Add as AddIcon } from '@material-ui/icons';
import type {
  PaginatedVideoSerializerWithCriteriaList,
  VideoSerializerWithCriteria,
  Video,
} from 'src/services/openapi';
import VideoCard from '../videos/VideoCard';
import { CompareNowAction } from 'src/utils/action';
import { UsersService } from 'src/services/openapi';
import { useLoginState } from 'src/hooks';

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
  const { isLoggedIn } = useLoginState();

  const AddToRateLaterList = ({ videoId }: { videoId: string }) => {
    const video_id = videoId;
    return (
      <div>
        {isLoggedIn && (
          <IconButton
            size="medium"
            color="secondary"
            onClick={async () => {
              await UsersService.usersMeVideoRateLaterCreate({
                video: { video_id } as Video,
              });
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
