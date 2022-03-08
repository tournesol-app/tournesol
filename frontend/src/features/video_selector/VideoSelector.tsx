import React, { useEffect, useMemo, useCallback, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Theme } from '@mui/material/styles';
import makeStyles from '@mui/styles/makeStyles';
import { AutoFixHigh as MagicWandIcon } from '@mui/icons-material';
import {
  IconButton,
  TextField,
  Tooltip,
  Box,
  Typography,
  Autocomplete,
} from '@mui/material';

import { UserRatingPublicToggle } from 'src/features/videos/PublicStatusAction';
import VideoCard, {
  EmptyVideoCard,
  VideoCardFromId,
} from 'src/features/videos/VideoCard';

import { ActionList } from 'src/utils/types';
import {
  extractVideoId,
  getVideoForComparison,
  idFromUid,
  isVideoIdValid,
} from 'src/utils/video';
import { UsersService, ContributorRating } from 'src/services/openapi';
import { UID_YT_NAMESPACE } from 'src/utils/constants';
import { videoFromRelatedEntity } from '../../utils/entity';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';

import SelectorListbox from './SelectorListbox';
import SelectorPopper from './SelectorPopper';
import VideoInput from './VideoInput';

// export const AutocompleteContext = React.createContext<{
//   open: boolean;
//   setOpen: (x: boolean) => void;
// }>({
//   open: false,
//   setOpen: function () {
//     return;
//   },
// });

const useStyles = makeStyles((theme: Theme) => ({
  root: {
    margin: 0,
  },
  controls: {
    margin: 4,
    display: 'flex',
    flexWrap: 'wrap',
    alignItems: 'center',
  },
  input: {
    [theme.breakpoints.down('sm')]: {
      fontSize: '0.7rem',
    },
  },
}));

interface Props {
  title: string;
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
  title,
  value,
  onChange,
  otherVideo,
  submitted = false,
}: Props) => {
  const { t } = useTranslation();

  const { videoId, rating } = value;
  const classes = useStyles();
  const [loading, setLoading] = useState(false);
  const { name: pollName } = useCurrentPoll();

  const loadRating = useCallback(async () => {
    setLoading(true);
    try {
      const contributorRating =
        await UsersService.usersMeContributorRatingsRetrieve({
          pollName,
          uid: UID_YT_NAMESPACE + videoId,
        });
      onChange({
        videoId,
        rating: contributorRating,
      });
    } catch (err) {
      if (err?.status === 404) {
        try {
          const contributorRating =
            await UsersService.usersMeContributorRatingsCreate({
              pollName,
              requestBody: {
                uid: UID_YT_NAMESPACE + videoId,
                is_public: true,
              },
            });
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
    setLoading(false);
  }, [pollName, videoId, onChange]);

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

  const handleChange = (value: string) => {
    const videoIdFromValue = extractVideoId(value);
    // if (videoIdFromValue) {
    //   setOpen(false);
    // }
    const newVideoId = videoIdFromValue
      ? videoIdFromValue
      : value.replace(/[^A-Za-z0-9-_]/g, '').substring(0, 11);
    onChange({
      videoId: newVideoId,
      rating: null,
    });
  };

  const handleRatingUpdate = useCallback(
    (newValue: ContributorRating) => {
      onChange({
        videoId: idFromUid(newValue.entity.uid),
        rating: newValue,
      });
    },
    [onChange]
  );

  const loadNewVideo = async () => {
    setLoading(true);
    const newVideoId: string | null = await getVideoForComparison(
      otherVideo,
      videoId
    );
    if (newVideoId) {
      onChange({
        videoId: newVideoId,
        rating: null,
      });
    } else {
      setLoading(false);
    }
  };

  const toggleAction: ActionList = useMemo(() => {
    return rating?.is_public != null
      ? [
          <UserRatingPublicToggle
            key="isPublicToggle"
            videoId={idFromUid(rating.entity.uid)}
            nComparisons={rating.n_comparisons}
            isPublic={rating.is_public}
            onChange={handleRatingUpdate}
          />,
        ]
      : [];
  }, [handleRatingUpdate, rating]);

  return (
    <div className={classes.root}>
      <Box m={0.5} display="flex" flexDirection="row" alignItems="center">
        <Typography variant="h5" color="text.secondary" flexGrow={1}>
          {title}
        </Typography>
        <Tooltip
          title={`${t('videoSelector.newVideo')}`}
          aria-label="new_video"
        >
          <IconButton aria-label="new_video" onClick={loadNewVideo}>
            <MagicWandIcon />
          </IconButton>
        </Tooltip>
      </Box>
      <Box m="4px">
        <VideoInput value={videoId} onChange={handleChange} />
      </Box>

      {rating ? (
        <VideoCard
          compact
          video={videoFromRelatedEntity(rating.entity)}
          settings={toggleAction}
        />
      ) : (
        <EmptyVideoCard compact loading={loading} />
      )}
    </div>
  );
};

export default VideoSelector;
