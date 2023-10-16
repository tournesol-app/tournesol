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

import {
  ContributorRating,
  ContributorCriteriaScore,
  TypeEnum,
} from 'src/services/openapi';
import {
  ActionList,
  EntityResult as EntityResult,
  JSONValue,
} from 'src/utils/types';
import { RatingControl } from 'src/features/ratings/RatingControl';

import EntityCardTitle from './EntityCardTitle';
import EntityCardScores from './EntityCardScores';
import EntityImagery from './EntityImagery';
import EntityMetadata, { VideoMetadata } from './EntityMetadata';
import EntityIndividualScores from './EntityIndividualScores';
import { entityCardMainSx } from './style';

export interface EntityCardProps {
  result: EntityResult;
  actions?: ActionList;
  compact?: boolean;
  isAvailable?: boolean;
  showRatingControl?: boolean;
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
  showRatingControl = false,
  onRatingChange,
}: EntityCardProps) => {
  const { t } = useTranslation();
  const theme = useTheme();
  const entity = result.entity;

  const isSmallScreen = useMediaQuery(theme.breakpoints.down('sm'), {
    noSsr: true,
  });

  const [contentDisplayed, setContentDisplayed] = useState(true);
  const [ratingVisible, setSettingsVisible] = useState(
    !isSmallScreen && showRatingControl
  );

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
            {isSmallScreen && showRatingControl && (
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
          {showRatingControl && (
            <Grid item xs={12}>
              <Collapse in={ratingVisible || !isSmallScreen}>
                <Box
                  paddingY={1}
                  borderTop="1px solid rgba(0, 0, 0, 0.12)"
                  display="flex"
                  gap="16px"
                  color="text.secondary"
                >
                  {'individual_rating' in result && (
                    <RatingControl
                      // Custom key to make sure the state is reset after rating has been updated by another component
                      key={`${entity.uid}__${result.individual_rating?.is_public}`}
                      uid={entity.uid}
                      individualRating={result.individual_rating}
                      onChange={onRatingChange}
                    />
                  )}
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
  individualScores,
}: {
  result: EntityResult;
  withLink?: boolean;
  individualScores?: ContributorCriteriaScore[];
}) => {
  const entity = result.entity;
  return (
    <Box
      display="flex"
      flexDirection="row"
      alignItems="center"
      gap={1}
      height="90px"
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
      <Stack gap="4px" alignSelf="start" marginTop={1} width="100%">
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
        {individualScores && (
          <EntityIndividualScores scores={individualScores} />
        )}
      </Stack>
    </Box>
  );
};

export default EntityCard;
