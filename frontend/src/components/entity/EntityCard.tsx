import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Box,
  Collapse,
  Grid,
  IconButton,
  useTheme,
  useMediaQuery,
  Stack,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
} from '@mui/icons-material';

import { TypeEnum } from 'src/services/openapi';
import { ActionList, JSONValue, RelatedEntityObject } from 'src/utils/types';

import EntityCardTitle from './EntityCardTitle';
import EntityCardScores from './EntityCardScores';
import EntityImagery from './EntityImagery';
import EntityMetadata, { VideoMetadata } from './EntityMetadata';
import { entityCardMainSx } from './style';

const EntityCard = ({
  entity,
  actions = [],
  settings = [],
  compact = false,
  entityTypeConfig,
}: {
  entity: RelatedEntityObject;
  actions?: ActionList;
  settings?: ActionList;
  compact?: boolean;
  // Configuration specific to the entity type.
  entityTypeConfig?: { [k in TypeEnum]?: { [k: string]: JSONValue } };
}) => {
  const { t } = useTranslation();
  const theme = useTheme();

  const isSmallScreen = useMediaQuery(theme.breakpoints.down('sm'), {
    noSsr: true,
  });
  const [settingsVisible, setSettingsVisible] = useState(!isSmallScreen);

  const displayEntityCardScores = () => {
    if ('tournesol_score' in entity && !compact) {
      return (
        <EntityCardScores
          entity={entity}
          showTournesolScore={entity.type !== TypeEnum.CANDIDATE_FR_2022}
          showTotalScore={entity.type === TypeEnum.CANDIDATE_FR_2022}
        />
      );
    }
    return null;
  };

  return (
    <Grid container sx={entityCardMainSx}>
      <Grid
        item
        xs={12}
        sm={compact ? 12 : 'auto'}
        sx={{
          display: 'flex',
          justifyContent: 'center',
          ...(compact ? {} : { minWidth: '240px', maxWidth: { sm: '240px' } }),
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
        {isSmallScreen && settings.length > 0 && (
          <>
            <Box flexGrow={1} />
            <IconButton
              size="small"
              aria-label={t('video.labelShowSettings')}
              onClick={() => setSettingsVisible(!settingsVisible)}
            >
              {settingsVisible ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            </IconButton>
          </>
        )}
      </Grid>
      {settings.length > 0 && (
        <Grid item xs={12}>
          <Collapse in={settingsVisible || !isSmallScreen}>
            <Box
              paddingY={1}
              borderTop="1px solid rgba(0, 0, 0, 0.12)"
              display="flex"
              gap="16px"
              color="text.secondary"
            >
              {settings.map((Action, index) =>
                typeof Action === 'function' ? (
                  <Action key={index} uid={entity.uid} />
                ) : (
                  Action
                )
              )}
            </Box>
          </Collapse>
        </Grid>
      )}
    </Grid>
  );
};

export const RowEntityCard = ({
  entity,
  withLink = false,
}: {
  entity: RelatedEntityObject;
  withLink?: boolean;
}) => {
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
      <Stack gap="4px">
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
