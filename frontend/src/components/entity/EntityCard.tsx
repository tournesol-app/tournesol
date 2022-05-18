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
import EntityCardScores from './EntityCardScores';
import { TypeEnum } from 'src/services/openapi';

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
        sx={{ display: 'flex', justifyContent: 'center' }}
      >
        <EntityImagery entity={entity} compact={compact} />
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

export default EntityCard;
