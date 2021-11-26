import React, {
  useState,
  useEffect,
  useCallback,
  useImperativeHandle,
} from 'react';

import { makeStyles } from '@material-ui/core/styles';
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

interface Props {
  videoId: string;
  setId: (pk: string) => void;
  otherVideo: string | null;
}

export interface VideoSelectorHandle {
  updateRating: () => void;
}

const VideoSelector = React.forwardRef<VideoSelectorHandle | undefined, Props>(
  ({ videoId, setId, otherVideo }: Props, ref) => {
    const classes = useStyles();
    const [rating, setRating] = useState<ContributorRating | null>(null);

    const loadRating = useCallback(async () => {
      if (!isVideoIdValid(videoId)) {
        setRating(null);
        return;
      }
      try {
        const contributorRating =
          await UsersService.usersMeContributorRatingsRetrieve(videoId);
        setRating(contributorRating);
      } catch (err) {
        if (err?.status === 404) {
          await ensureVideoExistsOrCreate(videoId);
          const contributorRating =
            await UsersService.usersMeContributorRatingsCreate({
              video_id: videoId,
            } as ContributorRatingCreate);
          setRating(contributorRating);
        } else {
          setRating(null);
        }
      }
    }, [videoId]);

    useEffect(() => {
      loadRating();
    }, [loadRating]);

    useImperativeHandle(
      ref,
      () => ({
        updateRating: loadRating,
      }),
      [loadRating]
    );

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
        </div>
        {rating ? (
          <VideoCard
            video={rating.video}
            compact
            settings={[
              () => (
                <>
                  {rating.is_public != null && (
                    <UserRatingPublicToggle
                      videoId={rating.video.video_id}
                      nComparisons={rating.n_comparisons}
                      isPublic={rating.is_public}
                    />
                  )}
                </>
              ),
            ]}
          />
        ) : (
          <EmptyVideoCard compact />
        )}
      </div>
    );
  }
);

VideoSelector.displayName = 'VideoSelector';
export default VideoSelector;
