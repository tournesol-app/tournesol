import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';

import {
  Box,
  Collapse,
  Grid2,
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
  EntityContext,
  OriginEnum,
  TypeEnum,
} from 'src/services/openapi';
import {
  ActionList,
  EntityResult as EntityResult,
  JSONValue,
} from 'src/utils/types';
import EntityCardContextAlert from 'src/features/entity_context/EntityCardContextAlert';
import { RatingControl } from 'src/features/ratings/RatingControl';

import EntityCardTitle from './EntityCardTitle';
import EntityCardScores from './EntityCardScores';
import EntityContextChip from './EntityContextChip';
import EntityImagery from './EntityImagery';
import EntityMetadata, {
  EntityMetadataVariant,
  VideoMetadata,
} from './EntityMetadata';
import EntityIndividualScores from './EntityIndividualScores';
import { entityCardMainSx } from './style';

export interface EntityCardProps {
  result: EntityResult;
  actions?: ActionList;
  compact?: boolean;
  isAvailable?: boolean;
  showEntitySeenIndicator?: boolean;
  showRatingControl?: boolean;
  onRatingChange?: (rating: ContributorRating) => void;
  // Configuration specific to the entity type.
  entityTypeConfig?: { [k in TypeEnum]?: { [k: string]: JSONValue } };
  displayContextAlert?: boolean;
  displayImage?: boolean;
}

const EntityCard = ({
  result,
  actions = [],
  compact = false,
  entityTypeConfig,
  isAvailable = true,
  showEntitySeenIndicator = false,
  showRatingControl = false,
  onRatingChange,
  displayContextAlert = false,
  displayImage = true,
}: EntityCardProps) => {
  const { t } = useTranslation();
  const theme = useTheme();

  const entity = result.entity;
  let unsafeContext: EntityContext | undefined;

  if ('entity_contexts' in result) {
    // TODO: when context from contribors are implemented, remove the
    // context.origin condition
    unsafeContext = result.entity_contexts.find(
      (context) => context.unsafe && context.origin === OriginEnum.ASSOCIATION
    );
  }

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

  const entitySeen =
    showEntitySeenIndicator &&
    'individual_rating' in result &&
    result.individual_rating?.entity_seen;

  return (
    <Grid2
      container
      sx={
        entitySeen
          ? {
              ...entityCardMainSx,
              borderBottom: '4px solid #b1e2b3',
            }
          : entityCardMainSx
      }
      direction={compact ? 'column' : 'row'}
    >
      {!isAvailable && (
        <Grid2
          container
          size={12}
          sx={{
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <Grid2
            sx={{
              pl: 1,
              py: 2,
            }}
          >
            <Typography>
              {entity.type == TypeEnum.VIDEO
                ? t('video.notAvailableAnymore')
                : t('entityCard.thisElementIsNotAvailable')}
            </Typography>
          </Grid2>
          <Grid2>
            <IconButton onClick={toggleEntityVisibility}>
              {contentDisplayed ? (
                <ArrowDropUp sx={{ color: 'rgba(0, 0, 0, 0.42)' }} />
              ) : (
                <ArrowDropDown sx={{ color: 'rgba(0, 0, 0, 0.42)' }} />
              )}
            </IconButton>
          </Grid2>
        </Grid2>
      )}
      {contentDisplayed && (
        <>
          {displayImage && (
            <Grid2
              sx={[
                {
                  display: 'flex',
                  justifyContent: 'center',
                },
                compact ? {} : { maxWidth: { sm: '240px' } },
              ]}
              size={{
                xs: 12,
                sm: compact ? 12 : 'auto',
              }}
            >
              <EntityImagery
                entity={entity}
                compact={compact}
                config={entityTypeConfig}
              />
            </Grid2>
          )}
          <Grid2
            data-testid="video-card-info"
            container
            direction="column"
            size="grow"
            sx={{
              p: 1,
              flexWrap: 'nowrap',
              lineHeight: '1.2',
            }}
          >
            <EntityCardTitle
              uid={entity.uid}
              title={entity.metadata.name}
              compact={compact}
            />
            <EntityMetadata entity={entity} />
            {displayEntityCardScores()}
          </Grid2>
          <Grid2
            sx={{
              display: 'flex',
              alignItems: 'end',
              justifyContent: 'start',
              flexDirection: 'column',
              [theme.breakpoints.down('sm')]: {
                flexDirection: 'row',
              },
            }}
            size={{
              xs: 12,
              sm: compact ? 12 : 1,
            }}
          >
            {actions.map((Action, index) =>
              typeof Action === 'function' ? (
                <Action key={index} uid={entity.uid} entity={result} />
              ) : (
                Action
              )
            )}
            {isSmallScreen && showRatingControl && (
              <>
                <Box
                  sx={{
                    flexGrow: 1,
                  }}
                />
                <IconButton
                  size="small"
                  aria-label={t('video.labelShowSettings')}
                  onClick={() => setSettingsVisible(!ratingVisible)}
                >
                  {ratingVisible ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                </IconButton>
              </>
            )}
          </Grid2>

          {displayContextAlert && unsafeContext && (
            <Grid2 size={12}>
              <EntityCardContextAlert uid={entity.uid} />
            </Grid2>
          )}

          {showRatingControl && (
            <Grid2 size={12}>
              <Collapse in={ratingVisible || !isSmallScreen}>
                <Box
                  sx={{
                    paddingY: 1,
                    borderTop: '1px solid rgba(0, 0, 0, 0.12)',
                    display: 'flex',
                    gap: '16px',
                    color: 'text.secondary',
                  }}
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
            </Grid2>
          )}
        </>
      )}
    </Grid2>
  );
};

export const RowEntityCard = ({
  result,
  withLink = false,
  individualScores,
  displayEntityContextChip = true,
  metadataVariant,
}: {
  result: EntityResult;
  withLink?: boolean;
  individualScores?: ContributorCriteriaScore[];
  displayEntityContextChip?: boolean;
  metadataVariant?: EntityMetadataVariant;
}) => {
  const entity = result.entity;

  const entitySeen =
    'individual_rating' in result && result.individual_rating?.entity_seen;

  let extraSx = {};
  if (entitySeen) {
    extraSx = {
      borderRight: '8px solid #b1e2b3',
    };
  }

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'row',
        alignItems: 'center',
        gap: 1,
        height: '90px',
        ...entityCardMainSx,
        bgcolor: 'transparent',
        ...extraSx,
      }}
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
      <Stack
        sx={{
          gap: '4px',
          alignSelf: 'start',
          marginTop: 1,
          width: '100%',
        }}
      >
        <EntityCardTitle
          uid={entity.uid}
          title={entity.metadata.name}
          titleMaxLines={1}
          withLink={withLink}
        />
        {entity.type == TypeEnum.VIDEO && (
          <VideoMetadata
            views={entity.metadata.views}
            uploader={entity.metadata.uploader}
            publicationDate={entity.metadata.publication_date}
            withLinks={false}
            variant={metadataVariant}
          />
        )}

        <Box
          sx={{
            pr: 1,
            display: 'flex',
            justifyContent: 'flex-end',
            gap: 1,
          }}
        >
          {displayEntityContextChip && 'entity_contexts' in result && (
            <EntityContextChip
              uid={result.entity.uid}
              entityContexts={result.entity_contexts}
            />
          )}
          {individualScores && (
            <EntityIndividualScores scores={individualScores} />
          )}
        </Box>
      </Stack>
    </Box>
  );
};

export default EntityCard;
