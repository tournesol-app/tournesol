import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link as RouterLink } from 'react-router-dom';
import makeStyles from '@mui/styles/makeStyles';
import {
  Grid,
  Box,
  Collapse,
  IconButton,
  useMediaQuery,
  useTheme,
  Theme,
} from '@mui/material';

import { ActionList, VideoObject } from 'src/utils/types';
import {
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
} from '@mui/icons-material';
import { videoIdFromEntity } from 'src/utils/video';
import VideoCardScores from './VideoCardScores';
import EntityCardTitle from 'src/components/entity/EntityCardTitle';
import { entityCardMainSx } from 'src/components/entity/style';
import { DurationWrapper } from 'src/components/entity/EntityImagery';
import { VideoMetadata } from 'src/components/entity/EntityMetadata';
import { useCurrentPoll } from 'src/hooks';
import { UID_YT_NAMESPACE } from 'src/utils/constants';

const useStyles = makeStyles((theme: Theme) => ({
  youtube_complements: {
    marginBottom: '8px',
    display: 'flex',
    flexWrap: 'wrap',
    alignContent: 'space-between',
    fontFamily: 'Poppins',
    fontSize: '0.8em',
    color: theme.palette.neutral.main,
  },
  youtube_complements_p: {
    marginRight: '12px',
  },
  top: {
    display: 'flex',
    flexWrap: 'wrap',
    alignContent: 'space-between',
  },
  settingsContainer: {
    '&.MuiGrid-item': {
      padding: 0,
    },
  },
}));

function VideoCard({
  video,
  actions = [],
  settings = [],
  compact = false,
  personalScore,
  showPlayer = true,
}: {
  video: VideoObject;
  actions?: ActionList;
  settings?: ActionList;
  compact?: boolean;
  personalScore?: number;
  showPlayer?: boolean;
}) {
  const theme = useTheme();
  const classes = useStyles();

  const { t } = useTranslation();
  const { baseUrl } = useCurrentPoll();

  const videoId = videoIdFromEntity(video);

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
            <RouterLink
              to={`${baseUrl}/entities/${UID_YT_NAMESPACE}${videoId}`}
              className="full-width"
            >
              <DurationWrapper duration={video.duration || undefined}>
                <img
                  className="full-width entity-thumbnail"
                  src={`https://i.ytimg.com/vi/${videoId}/mqdefault.jpg`}
                  alt={video.name}
                />
              </DurationWrapper>
            </RouterLink>
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
        <EntityCardTitle uid={video.uid} title={video.name} compact={compact} />
        <VideoMetadata
          views={video.views}
          publicationDate={video.publication_date}
          uploader={video.uploader}
        />
        {!compact && <VideoCardScores video={video} />}
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
            <Action key={index} uid={video.uid} />
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
        <Grid item xs={12} className={classes.settingsContainer}>
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
                  <Action key={index} uid={video.uid} />
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
