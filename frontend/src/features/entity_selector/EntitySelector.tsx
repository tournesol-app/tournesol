import React, { useEffect, useMemo, useCallback, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { Theme, useTheme } from '@mui/material/styles';
import makeStyles from '@mui/styles/makeStyles';
import { Box, Grid, Typography } from '@mui/material';

import { useCurrentPoll, useEntityAvailable, useLoginState } from 'src/hooks';
import { ENTITY_AVAILABILITY } from 'src/hooks/useEntityAvailable';
import { UserRatingPublicToggle } from 'src/features/videos/PublicStatusAction';
import EntityCard from 'src/components/entity/EntityCard';
import EmptyEntityCard from 'src/components/entity/EmptyEntityCard';

import { ActionList } from 'src/utils/types';
import {
  UsersService,
  ContributorRating,
  PollsService,
  Recommendation,
} from 'src/services/openapi';
import { UID_YT_NAMESPACE, YOUTUBE_POLL_NAME } from 'src/utils/constants';

import AutoEntityButton from './AutoEntityButton';
import EntitySelectButton from './EntitySelectButton';
import { extractVideoId } from 'src/utils/video';

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
  alignment?: 'left' | 'right';
  value: SelectorValue;
  onChange: (newValue: SelectorValue) => void;
  otherUid: string | null;
  variant?: 'regular' | 'noControl';
  autoFill?: boolean;
}

export interface SelectorValue {
  uid: string | null;
  rating: ContributorRating | null;
  ratingIsExpired?: boolean;
}

const isUidValid = (uid: string | null) =>
  uid === null ? false : uid.match(/\w+:.+/);

const EntitySelector = ({
  title,
  alignment = 'left',
  value,
  onChange,
  otherUid,
  variant = 'regular',
  autoFill = false,
}: Props) => {
  const classes = useStyles();
  const { isLoggedIn } = useLoginState();

  return (
    <div className={classes.root}>
      {isLoggedIn ? (
        <EntitySelectorInnerAuth
          title={title}
          value={value}
          onChange={onChange}
          otherUid={otherUid}
          alignment={alignment}
          variant={variant}
          autoFill={autoFill}
        />
      ) : (
        <EntitySelectorInnerAnonymous value={value} />
      )}
    </div>
  );
};

/**
 * Display the content of an EntitySelector for anonymous users.
 */
const EntitySelectorInnerAnonymous = ({ value }: { value: SelectorValue }) => {
  const { isLoggedIn } = useLoginState();
  const { name: pollName } = useCurrentPoll();

  const { uid } = value;
  const [entityFallback, setEntityFallback] = useState<Recommendation>();

  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function getEntity() {
      return await PollsService.pollsEntitiesRetrieve({
        name: pollName,
        uid: uid || '',
      });
    }

    // Wait for a not null / not empty UID before making an HTTP request.
    if (uid) {
      getEntity().then((entity) => {
        setLoading(false);
        setEntityFallback(entity);
      });
    }
  }, [isLoggedIn, pollName, uid]);

  return entityFallback ? (
    <EntityCard compact entity={entityFallback} settings={undefined} />
  ) : (
    <EmptyEntityCard compact loading={loading} />
  );
};

const EntitySelectorInnerAuth = ({
  title,
  value,
  onChange,
  otherUid,
  alignment,
  variant,
  autoFill,
}: Props) => {
  const theme = useTheme();
  const { t } = useTranslation();
  const { name: pollName, options } = useCurrentPoll();

  const { uid, rating, ratingIsExpired } = value;

  const [loading, setLoading] = useState(false);
  const [inputValue, setInputValue] = useState(value.uid);

  const { availability: entityAvailability } = useEntityAvailable(
    value.uid ?? ''
  );

  let showEntityInput = true;
  let showRatingControl = true;

  switch (variant) {
    case 'noControl':
      showEntityInput = false;
      showRatingControl = false;
  }

  const loadRating = useCallback(async () => {
    setLoading(true);
    try {
      const contributorRating =
        await UsersService.usersMeContributorRatingsRetrieve({
          pollName,
          uid: uid || '',
        });
      onChange({
        uid,
        rating: contributorRating,
        ratingIsExpired: false,
      });
    } catch (err) {
      if (err?.status === 404) {
        try {
          const contributorRating =
            await UsersService.usersMeContributorRatingsCreate({
              pollName,
              requestBody: {
                uid: uid || '',
                is_public: options?.comparisonsCanBePublic === true,
              },
            });
          onChange({
            uid,
            rating: contributorRating,
            ratingIsExpired: false,
          });
        } catch (err) {
          console.error('Failed to initialize contributor rating.', err);
        }
      } else {
        console.error('Failed to retrieve contributor rating.', err);
      }
    }
    setLoading(false);
  }, [onChange, options?.comparisonsCanBePublic, pollName, uid]);

  /**
   * Load the user's rating.
   */
  useEffect(() => {
    if (isUidValid(uid) && rating == null) {
      loadRating();
    }
  }, [loadRating, rating, uid]);

  /**
   * Reload rating after the parent (comparison) form has been submitted.
   */
  useEffect(() => {
    if (ratingIsExpired) {
      loadRating();
    }
  }, [loadRating, ratingIsExpired]);

  /**
   * Update input value when "uid" has been changed by the parent component.
   */
  useEffect(() => {
    setInputValue((previousValue) => {
      if (previousValue !== uid) {
        return uid;
      }
      return previousValue;
    });
  }, [uid]);

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
    <>
      {showEntityInput && (
        <>
          <Box
            m={1}
            display="flex"
            flexDirection={alignment === 'left' ? 'row' : 'row-reverse'}
            alignItems="center"
            justifyContent="space-between"
          >
            <Grid
              container
              spacing={1}
              display="flex"
              direction={alignment === 'left' ? 'row' : 'row-reverse'}
            >
              <Grid item>
                <EntitySelectButton
                  value={inputValue || uid || ''}
                  onChange={handleChange}
                  otherUid={otherUid}
                />
              </Grid>
              <Grid item>
                <AutoEntityButton
                  disabled={loading}
                  currentUid={uid}
                  otherUid={otherUid}
                  onClick={() => {
                    setLoading(true);
                    setInputValue('');
                  }}
                  onResponse={(uid) => {
                    uid ? onChange({ uid, rating: null }) : setLoading(false);
                  }}
                  autoFill={autoFill}
                />
              </Grid>
            </Grid>
            <Typography
              variant="h6"
              color="secondary"
              sx={{ '&:first-letter': { textTransform: 'capitalize' } }}
            >
              {title}
            </Typography>
          </Box>
        </>
      )}
      <Box position="relative">
        {rating ? (
          <EntityCard
            compact
            entity={rating.entity}
            settings={showRatingControl ? toggleAction : undefined}
          ></EntityCard>
        ) : (
          <EmptyEntityCard compact loading={loading} />
        )}
        {entityAvailability === ENTITY_AVAILABILITY.UNAVAILABLE && !loading && (
          <Box
            display="flex"
            justifyContent="center"
            alignItems="center"
            position="absolute"
            top="0"
            color="white"
            bgcolor="rgba(0,0,0,.6)"
            width="100%"
            sx={{
              aspectRatio: '16/9',
              [theme.breakpoints.down('sm')]: {
                fontSize: '0.8rem',
              },
            }}
          >
            <Typography textAlign="center" fontSize="inherit">
              {pollName === YOUTUBE_POLL_NAME
                ? t('entitySelector.youtubeVideoUnavailable')
                : t('entityCard.thisElementIsNotAvailable')}
            </Typography>
          </Box>
        )}
      </Box>
    </>
  );
};

export default EntitySelector;
