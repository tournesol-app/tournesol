import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Box,
  Collapse,
  Grid,
  IconButton,
  useTheme,
  useMediaQuery,
  Stack,
  Typography,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  ArrowDropDown,
  ArrowDropUp,
} from '@mui/icons-material';

import { ContributorRating, TypeEnum } from 'src/services/openapi';
import {
  ActionList,
  EntityResult as EntityResult,
  JSONValue,
} from 'src/utils/types';
import { UserRatingPublicToggle } from 'src/features/videos/PublicStatusAction';

import EntityCardTitle from './EntityCardTitle';
import EntityCardScores from './EntityCardScores';
import EntityImagery from './EntityImagery';
import EntityMetadata, { VideoMetadata } from './EntityMetadata';
import { entityCardMainSx } from './style';

export interface EntityCardProps {
  result: EntityResult;
  actions?: ActionList;
  compact?: boolean;
  isAvailable?: boolean;
  withRatingStatus?: boolean;
  onRatingChange?: (rating: ContributorRating) => void;
  // Configuration specific to the entity type.
  entityTypeConfig?: { [k in TypeEnum]?: { [k: string]: JSONValue } };
}

const EntityCard = ({
  result,
  actions = [],
  compact = false,
  entityTypeConfig,
  isAvailable = true,
  withRatingStatus = false,
  onRatingChange,
}: EntityCardProps) => {
  const { t } = useTranslation();
  const theme = useTheme();
  const entity = result.entity;

  const isSmallScreen = useMediaQuery(theme.breakpoints.down('sm'), {
    noSsr: true,
  });

  const [contentDisplayed, setContentDisplayed] = useState(true);
  const [ratingVisible, setSettingsVisible] = useState(!isSmallScreen);

  useEffect(() => {
    setContentDisplayed(isAvailable);
  }, [isAvailable]);

  const displayEntityCardScores = () => {
    if ('collective_rating' in result && !compact) {
      return (
        <EntityCardScores
          result={result}
          showTournesolScore={entity.type !== TypeEnum.CANDIDATE_FR_2022}
          showTotalScore={entity.type === TypeEnum.CANDIDATE_FR_2022}
        />
      );
    }
    return null;
  };

  const toggleEntityVisibility = () => {
    setContentDisplayed(!contentDisplayed);
  };

  return (
    <Grid container sx={entityCardMainSx}>
      {!isAvailable && (
        <Grid container justifyContent="space-between" alignItems="center">
          <Grid item pl={1} py={2}>
            <Typography>
              {entity.type == TypeEnum.VIDEO
                ? t('video.notAvailableAnymore')
                : t('entityCard.thisElementIsNotAvailable')}
            </Typography>
          </Grid>
          <Grid item>
            <IconButton onClick={toggleEntityVisibility}>
              {contentDisplayed ? (
                <ArrowDropUp sx={{ color: 'rgba(0, 0, 0, 0.42)' }} />
              ) : (
                <ArrowDropDown sx={{ color: 'rgba(0, 0, 0, 0.42)' }} />
              )}
            </IconButton>
          </Grid>
        </Grid>
      )}
      {contentDisplayed && (
        <>
          <Grid
            item
            xs={12}
            sm={compact ? 12 : 'auto'}
            sx={{
              display: 'flex',
              justifyContent: 'center',
              ...(compact
                ? {}
                : { minWidth: '240px', maxWidth: { sm: '240px' } }),
            }}
          >
            <EntityImagery
              entity={entity}
              compact={compact}
              config={entityTypeConfig}
            />
          </Grid>
          <Grid
            item
            xs={12}
            sm={compact ? 12 : true}
            sx={{
              padding: 1,
            }}
            data-testid="video-card-info"
            container
            direction="column"
          >
            <EntityCardTitle
              uid={entity.uid}
              title={entity.metadata.name}
              compact={compact}
            />
            <EntityMetadata entity={entity} />
            {displayEntityCardScores()}
          </Grid>
          <Grid
            item
            xs={12}
            sm={compact ? 12 : 1}
            sx={{
              display: 'flex',
              alignItems: 'end',
              justifyContent: 'space-between',
              flexDirection: 'column',
              [theme.breakpoints.down('sm')]: {
                flexDirection: 'row',
              },
            }}
          >
            {actions.map((Action, index) =>
              typeof Action === 'function' ? (
                <Action key={index} uid={entity.uid} />
              ) : (
                Action
              )
            )}
            {isSmallScreen && withRatingStatus && (
              <>
                <Box flexGrow={1} />
                <IconButton
                  size="small"
                  aria-label={t('video.labelShowSettings')}
                  onClick={() => setSettingsVisible(!ratingVisible)}
                >
                  {ratingVisible ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                </IconButton>
              </>
            )}
          </Grid>
          {withRatingStatus && (
            <Grid item xs={12}>
              <Collapse in={ratingVisible || !isSmallScreen}>
                <Box
                  paddingY={1}
                  borderTop="1px solid rgba(0, 0, 0, 0.12)"
                  display="flex"
                  gap="16px"
                  color="text.secondary"
                >
                  <>
                    {/* {settings.map((Action, index) =>
                      typeof Action === 'function' ? (
                        <Action key={index} uid={entity.uid} />
                      ) : (
                        Action
                      )
                    )} */}
                    {'individual_rating' in result &&
                      result.individual_rating && (
                        <UserRatingPublicToggle
                          // Custom key to make sure the state is reset after rating has been updated by another component
                          key={`${entity.uid}__${result.individual_rating.is_public}`}
                          uid={entity.uid}
                          nComparisons={result.individual_rating.n_comparisons}
                          initialIsPublic={result.individual_rating.is_public}
                          onChange={onRatingChange}
                        />
                      )}
                  </>
                </Box>
              </Collapse>
            </Grid>
          )}
        </>
      )}
    </Grid>
  );
};

export const RowEntityCard = ({
  result,
  withLink = false,
}: {
  result: EntityResult;
  withLink?: boolean;
}) => {
  const entity = result.entity;
  return (
    <Box
      display="flex"
      flexDirection="row"
      alignItems="center"
      gap={1}
      height="70px"
      sx={{ ...entityCardMainSx, bgcolor: 'transparent' }}
    >
      <Box sx={{ aspectRatio: '16 / 9', height: '100%' }}>
        <EntityImagery
          entity={entity}
          config={{
            [TypeEnum.VIDEO]: {
              displayPlayer: false,
              thumbnailLink: withLink,
            },
          }}
        />
      </Box>
      <Stack gap="4px" alignSelf="start" marginTop={1}>
        <EntityCardTitle
          uid={entity.uid}
          title={entity.metadata.name}
          titleMaxLines={1}
          withLink={withLink}
          fontSize="1em"
        />
        {entity.type == TypeEnum.VIDEO && (
          <VideoMetadata
            views={entity.metadata.views}
            uploader={entity.metadata.uploader}
            publicationDate={entity.metadata.publication_date}
            withLinks={false}
          />
        )}
      </Stack>
    </Box>
  );
};

export default EntityCard;
