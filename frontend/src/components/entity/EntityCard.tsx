import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Box,
  Collapse,
  Grid,
  IconButton,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
} from '@mui/icons-material';

import EntityCardTitle from './EntityCardTitle';
import EntityImagery from './EntityImagery';
import EntityMetadata from './EntityMetadata';
import { entityCardMainSx } from './style';
import { RelatedEntityObject, ActionList } from 'src/utils/types';

const EntityCard = ({
  entity,
  actions = [],
  settings = [],
  compact = false,
}: {
  entity: RelatedEntityObject;
  actions?: ActionList;
  settings?: ActionList;
  compact?: boolean;
}) => {
  const { t } = useTranslation();
  const theme = useTheme();

  const isSmallScreen = useMediaQuery(theme.breakpoints.down('sm'), {
    noSsr: true,
  });
  const [settingsVisible, setSettingsVisible] = useState(!isSmallScreen);

  return (
    <Grid container sx={entityCardMainSx}>
      <Grid item xs={12} sm={4} md={3} sx={{ aspectRatio: '16 / 9' }}>
        <EntityImagery entity={entity} />
      </Grid>
      <Grid
        item
        xs={12}
        sm={8}
        md={9}
        sx={{
          padding: 1,
        }}
        data-testid="video-card-info"
        container
        direction="column"
      >
        <EntityCardTitle title={entity.metadata.name} compact={compact} />
        <EntityMetadata entity={entity} />
        {/* TODO: implement scores in this entity card}
        {/* {!compact && <VideoCardScores video={video} />} */}
      </Grid>
      <Grid
        item
        xs={12}
        sm={compact ? 12 : 1}
        sx={{
          display: 'flex',
          alignItems: 'end',
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

export default EntityCard;
