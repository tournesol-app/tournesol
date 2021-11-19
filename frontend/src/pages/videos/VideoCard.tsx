import React from 'react';

import { makeStyles } from '@material-ui/core/styles';
import { useParams } from 'react-router-dom';
import VideoCard from 'src/features/videos/VideoCard';
import { useVideoMetadata } from 'src/features/videos/VideoApi';

const useStyles = makeStyles(() => ({
  root: {
    width: '100%',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    minWidth: '420px',
    marginTop: 120,
  },
}));

const VideoCardFromId = ({ videoId }: { videoId: string }) => {
  const video = useVideoMetadata(videoId);
  return <VideoCard video={video} />;
};

function VideoCardPage() {
  const classes = useStyles();
  const { video_id } = useParams<{ video_id: string }>();

  return (
    <div>
      <div className={classes.root}>
        <VideoCardFromId videoId={video_id} />
      </div>
    </div>
  );
}

export default VideoCardPage;
