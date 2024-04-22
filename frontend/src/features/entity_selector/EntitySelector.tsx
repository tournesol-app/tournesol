import React, { useEffect, useCallback, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useDrag } from '@use-gesture/react';
import { Vector2 } from '@use-gesture/core/types';

import { useTheme } from '@mui/material/styles';
import { Box, Grid, Slide, Typography } from '@mui/material';

import { useCurrentPoll, useEntityAvailable, useLoginState } from 'src/hooks';
import { ENTITY_AVAILABILITY } from 'src/hooks/useEntityAvailable';
import EntityCard from 'src/components/entity/EntityCard';
import EmptyEntityCard from 'src/components/entity/EmptyEntityCard';
import { SuggestionHistory } from 'src/features/suggestions/suggestionHistory';
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
import { entityCardMainSx } from 'src/components/entity/style';

const ENTITY_CARD_SWIPE_TIMEOUT = 180;
// The minimum velocity per axis in pixels / ms.
const ENTITY_CARD_SWIPE_VELOCITY: number | Vector2 = [0.25, 0.25];

interface Props {
  alignment?: 'left' | 'right';
  value: SelectorValue;
  onChange: (newValue: SelectorValue) => void;
  otherUid: string | null;
  variant?: 'regular' | 'noControl';
  history?: SuggestionHistory;
}

export interface SelectorValue {
  uid: string | null;
  rating: ContributorRating | null;
  ratingIsExpired?: boolean;
}

const isUidValid = (uid: string | null) =>
  uid === null ? false : uid.match(/\w+:.+/);

const EntitySelector = ({
  alignment = 'left',
  value,
  onChange,
  otherUid,
  variant = 'regular',
  history,
}: Props) => {
  const { isLoggedIn } = useLoginState();

  return (
    <>
      {isLoggedIn ? (
        <EntitySelectorInnerAuth
          value={value}
          onChange={onChange}
          otherUid={otherUid}
          alignment={alignment}
          variant={variant}
          history={history}
        />
      ) : (
        <EntitySelectorInnerAnonymous value={value} />
      )}
    </>
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
    <EntityCard compact result={entityFallback} />
  ) : (
    <EmptyEntityCard compact loading={loading} />
  );
};

const EntitySelectorInnerAuth = ({
  value,
  onChange,
  otherUid,
  alignment,
  variant,
  history,
}: Props) => {
  const theme = useTheme();
  const { t } = useTranslation();
  const { name: pollName, options } = useCurrentPoll();

  const { uid, rating, ratingIsExpired } = value;

  const [slideIn, setSlideIn] = useState(true);
  const [slideDirection, setSlideDirection] = useState<'up' | 'down'>('down');

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
    setSlideIn(true);
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

  const bindDrag = useDrag(
    ({ swipe, type }) => {
      if (variant === 'noControl' || slideIn === false) {
        return;
      }

      if (type === 'pointerup' || type === 'touchend') {
        // On swipe up
        if (swipe[1] < 0) {
          slideUp();
        }
        // On swipe down
        if (swipe[1] > 0) {
          slideDown();
        }
      }
    },
    { swipe: { velocity: ENTITY_CARD_SWIPE_VELOCITY } }
  );

  const onSlideEntered = () => {
    setSlideDirection('down');
    setLoading(false);
  };

  const onSlideExited = async () => {
    if (slideDirection === 'up') {
      const newUid = await history?.nextLeftOrSuggestion(pollName, [
        uid,
        otherUid,
      ]);

      if (newUid) {
        setSlideDirection('down');
        onChange({ uid: newUid, rating: null });
      } else {
        setSlideIn(true);
      }
    } else {
      const newUid = await history?.nextRightOrSuggestion(pollName, [
        uid,
        otherUid,
      ]);

      if (newUid) {
        setSlideDirection('up');
        onChange({ uid: newUid, rating: null });
      } else {
        console.warn('No entity found by the function nextSuggestion.');
        setSlideIn(true);
      }
    }
  };

  const slideUp = async () => {
    if (loading || !slideIn) {
      return;
    }

    setSlideDirection('down');
    setLoading(true);
    setInputValue('');
    setSlideIn(false);
  };

  const slideDown = () => {
    if (loading || !slideIn) {
      return;
    }

    setSlideDirection('up');
    setLoading(true);
    setInputValue('');
    setSlideIn(false);
  };

  return (
    <>
      {showEntityInput && (
        <Box
          mb={{ xs: '4px', sm: 1 }}
          display="flex"
          flexDirection={
            uid
              ? alignment === 'left'
                ? 'row'
                : 'row-reverse'
              : alignment !== 'left'
              ? 'row'
              : 'row-reverse'
          }
          alignItems="center"
          justifyContent="space-between"
        >
          <Grid
            container
            spacing={1}
            display={uid ? 'flex' : 'none'}
            direction={alignment === 'left' ? 'row' : 'row-reverse'}
            justifyContent={{ xs: 'space-around', sm: 'flex-start' }}
          >
            <Grid item>
              <EntitySelectButton
                value={inputValue || uid || ''}
                onChange={handleChange}
                otherUid={otherUid}
                history={history}
              />
            </Grid>
            <Grid item>
              <AutoEntityButton disabled={loading} onClick={slideUp} />
            </Grid>
          </Grid>
        </Box>
      )}
      <Slide
        mountOnEnter
        in={slideIn}
        direction={slideDirection}
        onEntered={onSlideEntered}
        onExited={onSlideExited}
        timeout={ENTITY_CARD_SWIPE_TIMEOUT}
        appear={false}
      >
        <Box
          {...bindDrag()}
          sx={{ touchAction: 'none' }}
          // "flex" properties allow the cards to be flexible and both cards to keep the same height.
          // "position: relative" is required to correctly display the entity unavailable box.
          display="flex"
          flex={1}
          position="relative"
        >
          {rating ? (
            <EntityCard
              compact
              result={rating}
              showRatingControl={showRatingControl}
              onRatingChange={handleRatingUpdate}
            ></EntityCard>
          ) : (
            <>
              {(loading ||
                !showEntityInput ||
                entityAvailability === ENTITY_AVAILABILITY.UNAVAILABLE) && (
                <EmptyEntityCard compact loading={loading} />
              )}
              {!loading &&
                entityAvailability === ENTITY_AVAILABILITY.UNAVAILABLE && (
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
              <Grid
                container
                sx={{
                  ...entityCardMainSx,
                  display:
                    uid ||
                    loading ||
                    !showEntityInput ||
                    entityAvailability === ENTITY_AVAILABILITY.UNAVAILABLE
                      ? 'none'
                      : 'flex',
                }}
              >
                <Grid
                  container
                  item
                  xs={12}
                  sx={{
                    aspectRatio: '16 / 9',
                    backgroundColor: '#fafafa',
                  }}
                  spacing={1}
                  alignItems="center"
                  justifyContent="space-around"
                  wrap="wrap"
                >
                  <Grid container item xs={12} sm={5} justifyContent="center">
                    <EntitySelectButton
                      value={inputValue || uid || ''}
                      onChange={handleChange}
                      otherUid={otherUid}
                      variant="full"
                    />
                  </Grid>
                  <Grid container item xs={12} sm={5} justifyContent="center">
                    <AutoEntityButton
                      disabled={loading}
                      onClick={slideUp}
                      variant="full"
                    />
                  </Grid>
                </Grid>
              </Grid>
            </>
          )}
        </Box>
      </Slide>
    </>
  );
};

export default EntitySelector;
