import React from 'react';
import ReactPlayer from 'react-player/youtube';

import { makeStyles } from '@material-ui/core/styles';
import ReplayIcon from '@material-ui/icons/Replay';
import IconButton from '@material-ui/core/IconButton';
import TextField from '@material-ui/core/TextField';
import Tooltip from '@material-ui/core/Tooltip';

import { extractVideoId } from 'src/utils/video';
import { getVideoForComparison } from 'src/utils/video';

const useStyles = makeStyles(() => ({
  root: {
    margin: 4,
  },
  playerWrapper: {
    position: 'relative',
    aspectRatio: '16 / 9',
  },
  reactPlayer: {
    position: 'absolute',
    top: 0,
    left: 0,
  },
  controls: {
    marginTop: '12px',
    display: 'flex',
    flexWrap: 'wrap',
  },
}));

const VideoSelector = ({
  videoId,
  setId,
  otherVideo,
}: {
  videoId: string | null;
  setId: (pk: string) => void;
  otherVideo: string | null;
}) => {
  const classes = useStyles();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const videoId = extractVideoId(e.target.value);
    const _videoId = videoId
      ? videoId
      : e.target.value.replace(/[^A-Za-z0-9-_]/g, '').substring(0, 11);
    setId(_videoId);
  };

  const loadNewVideo = async () => {
    const newVideoId: string | null = await getVideoForComparison(
      otherVideo,
      videoId
    );
    if (newVideoId) setId(newVideoId);
  };

  return (
    <div className={classes.root}>
      {videoId && (
        <div className={classes.playerWrapper}>
          <ReactPlayer
            url={`https://youtube.com/watch?v=${videoId}`}
            controls
            light
            width="100%"
            height="100%"
            className={classes.reactPlayer}
          />
        </div>
      )}
      <div className={classes.controls}>
        <TextField
          placeholder="Paste URL or Video ID"
          style={{ flex: 1, minWidth: '10em' }}
          value={videoId || ''}
          onChange={handleChange}
        />
        <Tooltip title="New Video" aria-label="new_video">
          <IconButton aria-label="new_video" onClick={loadNewVideo}>
            <ReplayIcon />
          </IconButton>
        </Tooltip>
        {/* TODO: re-enable privacy options <PrivacyStatusSelector id={id} /> */}
      </div>
    </div>
  );
};

export default VideoSelector;
