import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Grid,
  Box,
  Collapse,
  IconButton,
  useMediaQuery,
  useTheme,
} from '@mui/material';

import { ActionList } from 'src/utils/types';
import { Recommendation } from 'src/services/openapi';
import {
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
} from '@mui/icons-material';
import EntityCardTitle from 'src/components/entity/EntityCardTitle';
import EntityCardScores from 'src/components/entity/EntityCardScores';
import { InternalLink } from 'src/components';
import { entityCardMainSx } from 'src/components/entity/style';
import { DurationWrapper } from 'src/components/entity/EntityImagery';
import { VideoMetadata } from 'src/components/entity/EntityMetadata';
import { useCurrentPoll } from 'src/hooks';
import { UID_YT_NAMESPACE } from 'src/utils/constants';

function VideoCard({
  video,
  actions = [],
  settings = [],
  compact = false,
  personalScore,
  showPlayer = true,
}: {
  video: Recommendation;
  actions?: ActionList;
  settings?: ActionList;
  compact?: boolean;
  personalScore?: number;
  showPlayer?: boolean;
}) {
  const theme = useTheme();

  const { t } = useTranslation();
  const { baseUrl } = useCurrentPoll();

  const entity = video.entity;
  const videoId = entity.metadata.video_id;

  const isSmallScreen = useMediaQuery(theme.breakpoints.down('sm'), {
    noSsr: true,
  });
  const [settingsVisible, setSettingsVisible] = useState(!isSmallScreen);

  return (
    <Grid container sx={entityCardMainSx}>
      {showPlayer && (
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
          <Box
            display="flex"
            alignItems="center"
            bgcolor="black"
            width="100%"
            // prevent the RouterLink to add few extra pixels
            lineHeight={0}
            sx={{
              '& > img': {
                flex: 1,
              },
            }}
          >
            <InternalLink
              to={`${baseUrl}/entities/${UID_YT_NAMESPACE}${videoId}`}
              sx={{ width: '100%' }}
            >
              <DurationWrapper duration={entity.metadata.duration || undefined}>
                <img
                  className="full-width entity-thumbnail"
                  src={`https://i.ytimg.com/vi/${videoId}/mqdefault.jpg`}
                  alt={entity.metadata.name}
                />
              </DurationWrapper>
            </InternalLink>
          </Box>
        </Grid>
      )}
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
        <VideoMetadata
          views={entity.metadata.views}
          publicationDate={entity.metadata.publication_date}
          uploader={entity.metadata.uploader}
        />
        {!compact && <EntityCardScores result={video} />}
        {personalScore !== undefined &&
          t('video.personalScore', { score: personalScore.toFixed(0) })}
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
        <Grid item xs={12} p={0}>
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
}

export default VideoCard;
