import React, { useEffect, useMemo, useCallback } from 'react';

import { makeStyles, Theme } from '@material-ui/core/styles';
import ReplayIcon from '@material-ui/icons/Replay';
import IconButton from '@material-ui/core/IconButton';
import TextField from '@material-ui/core/TextField';
import Tooltip from '@material-ui/core/Tooltip';

import { extractVideoId, isVideoIdValid } from 'src/utils/video';
import { getVideoForComparison } from 'src/utils/video';
import VideoCard, { EmptyVideoCard } from '../videos/VideoCard';
import {
  UsersService,
  ContributorRating,
  ContributorRatingCreate,
} from 'src/services/openapi';
import { UserRatingPublicToggle } from '../videos/PublicStatusAction';
import { ensureVideoExistsOrCreate } from 'src/utils/video';
import { ActionList } from 'src/utils/types';

const useStyles = makeStyles((theme: Theme) => ({
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
    display: 'flex',
    flexWrap: 'wrap',
    padding: '4px 0',
    alignItems: 'center',
  },
  input: {
    [theme.breakpoints.down('xs')]: {
      fontSize: '0.7rem',
    },
  },
}));

interface Props {
  value: VideoSelectorValue;
  onChange: (newValue: VideoSelectorValue) => void;
  otherVideo: string | null;
  submitted?: boolean;
}

export interface VideoSelectorValue {
  videoId: string;
  rating: ContributorRating | null;
}

const VideoSelector = ({
  value,
  onChange,
  otherVideo,
  submitted = false,
}: Props) => {
  const { videoId, rating } = value;
  const classes = useStyles();

  const loadRating = useCallback(async () => {
    try {
      const contributorRating =
        await UsersService.usersMeContributorRatingsRetrieve(videoId);
      onChange({
        videoId,
        rating: contributorRating,
      });
    } catch (err) {
      if (err?.status === 404) {
        try {
          await ensureVideoExistsOrCreate(videoId);
          const contributorRating =
            await UsersService.usersMeContributorRatingsCreate({
              video_id: videoId,
            } as ContributorRatingCreate);
          onChange({
            videoId,
            rating: contributorRating,
          });
        } catch (err) {
          console.error('Failed to initialize contributor rating.', err);
        }
      } else {
        console.error('Failed to retrieve contributor rating.', err);
      }
    }
  }, [videoId, onChange]);

  useEffect(() => {
    if (isVideoIdValid(videoId) && rating == null) {
      loadRating();
    }
  }, [loadRating, videoId, rating]);

  useEffect(() => {
    // Reload rating after the parent (comparison) form has been submitted.
    if (submitted) {
      loadRating();
    }
  }, [loadRating, submitted]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const videoIdFromValue = extractVideoId(e.target.value);
    const newVideoId = videoIdFromValue
      ? videoIdFromValue
      : e.target.value.replace(/[^A-Za-z0-9-_]/g, '').substring(0, 11);
    onChange({
      videoId: newVideoId,
      rating: null,
    });
  };

  const handleRatingUpdate = useCallback(
    (newValue: ContributorRating) => {
      onChange({
        videoId: newValue.video.video_id,
        rating: newValue,
      });
    },
    [onChange]
  );

  const loadNewVideo = async () => {
    const newVideoId: string | null = await getVideoForComparison(
      otherVideo,
      videoId
    );
    if (newVideoId) {
      onChange({
        videoId: newVideoId,
        rating: null,
      });
    }
  };

  const toggleAction: ActionList = useMemo(() => {
    return rating?.is_public != null
      ? [
          <UserRatingPublicToggle
            key="isPublicToggle"
            videoId={rating.video.video_id}
            nComparisons={rating.n_comparisons}
            isPublic={rating.is_public}
            onChange={handleRatingUpdate}
          />,
        ]
      : [];
  }, [handleRatingUpdate, rating]);

  return (
    <div className={classes.root}>
      <div className={classes.controls}>
        <TextField
          InputProps={{ classes: { input: classes.input } }}
          placeholder="Paste URL or Video ID"
          style={{ flex: 1 }}
          value={videoId || ''}
          onChange={handleChange}
        />
        <Tooltip title="New Video" aria-label="new_video">
          <IconButton aria-label="new_video" onClick={loadNewVideo}>
            <ReplayIcon />
          </IconButton>
        </Tooltip>
      </div>
      {rating ? (
        <VideoCard compact video={rating.video} settings={toggleAction} />
      ) : (
        <EmptyVideoCard compact />
      )}
    </div>
  );
};

export default VideoSelector;
