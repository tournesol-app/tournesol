import React, { useEffect, useMemo, useCallback, useState } from 'react';
import { Theme } from '@mui/material/styles';
import makeStyles from '@mui/styles/makeStyles';
import { Box, Typography } from '@mui/material';

import { UserRatingPublicToggle } from 'src/features/videos/PublicStatusAction';
import VideoCard, { EmptyVideoCard } from 'src/features/videos/VideoCard';

import { ActionList } from 'src/utils/types';
import { extractVideoId } from 'src/utils/video';
import { UsersService, ContributorRating } from 'src/services/openapi';
import { UID_YT_NAMESPACE, YOUTUBE_POLL_NAME } from 'src/utils/constants';
import { videoFromRelatedEntity } from '../../utils/entity';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import AutoEntityButton from './AutoEntityButton';

import VideoInput from './VideoInput';

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
  value: SelectorValue;
  onChange: (newValue: SelectorValue) => void;
  otherUid: string | null;
  submitted?: boolean;
}

export interface SelectorValue {
  uid: string;
  rating: ContributorRating | null;
}

const isUidValid = (uid: string) => uid.match(/\w+:.+/);

const VideoSelector = ({
  title,
  value,
  onChange,
  otherUid,
  submitted = false,
}: Props) => {
  const { uid, rating } = value;
  const classes = useStyles();
  const [loading, setLoading] = useState(false);
  const { name: pollName } = useCurrentPoll();
  const [inputValue, setInputValue] = useState(value.uid);

  const loadRating = useCallback(async () => {
    setLoading(true);
    try {
      const contributorRating =
        await UsersService.usersMeContributorRatingsRetrieve({
          pollName,
          uid,
        });
      onChange({
        uid,
        rating: contributorRating,
      });
    } catch (err) {
      if (err?.status === 404) {
        try {
          const contributorRating =
            await UsersService.usersMeContributorRatingsCreate({
              pollName,
              requestBody: {
                uid,
                is_public: true,
              },
            });
          onChange({
            uid,
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
  }, [pollName, uid, onChange]);

  useEffect(() => {
    if (isUidValid(uid) && rating == null) {
      loadRating();
    }
  }, [loadRating, uid, rating]);

  useEffect(() => {
    // Reload rating after the parent (comparison) form has been submitted.
    if (submitted) {
      loadRating();
    }
  }, [loadRating, submitted]);

  const handleChange = (value: string) => {
    if (value === '') {
      setInputValue('');
      onChange({
        uid: '',
        rating: null,
      });
      return;
    }

    const videoIdFromValue =
      pollName === YOUTUBE_POLL_NAME ? extractVideoId(value) : null;
    const newUid = videoIdFromValue
      ? UID_YT_NAMESPACE + videoIdFromValue
      : value.trim();
    setInputValue(newUid);
    onChange({
      uid: newUid,
      rating: null,
    });
  };

  const handleRatingUpdate = useCallback(
    (newValue: ContributorRating) => {
      onChange({
        uid: newValue.entity.uid,
        rating: newValue,
      });
    },
    [onChange]
  );

  const toggleAction: ActionList = useMemo(() => {
    return rating?.is_public != null
      ? [
          <UserRatingPublicToggle
            key="isPublicToggle"
            uid={rating.entity.uid}
            nComparisons={rating.n_comparisons}
            isPublic={rating.is_public}
            onChange={handleRatingUpdate}
          />,
        ]
      : [];
  }, [handleRatingUpdate, rating]);

  return (
    <div className={classes.root}>
      <Box
        mx={1}
        marginTop="4px"
        display="flex"
        flexDirection="row"
        alignItems="center"
      >
        <Typography variant="h5" color="text.disabled" flexGrow={1}>
          {title}
        </Typography>
        <AutoEntityButton
          currentUid={uid}
          otherUid={otherUid}
          onClick={() => {
            setInputValue('');
            setLoading(true);
          }}
          onResponse={(uid) => {
            uid ? onChange({ uid, rating: null }) : setLoading(false);
          }}
        />
      </Box>
      <Box mx={1} marginBottom={1}>
        <VideoInput value={inputValue || uid} onChange={handleChange} />
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
