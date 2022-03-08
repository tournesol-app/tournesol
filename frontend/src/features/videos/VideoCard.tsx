import React, { useState } from 'react';
import ReactPlayer from 'react-player/youtube';
import { Link as RouterLink } from 'react-router-dom';
import { useTranslation, Trans } from 'react-i18next';
import makeStyles from '@mui/styles/makeStyles';
import {
  Grid,
  Box,
  Collapse,
  IconButton,
  useMediaQuery,
  useTheme,
  Tooltip,
  Link,
  Stack,
} from '@mui/material';
import { Warning as WarningIcon } from '@mui/icons-material';

import { ActionList, VideoObject } from 'src/utils/types';
import { useVideoMetadata } from './VideoApi';
import {
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
} from '@mui/icons-material';
import {
  convertDurationToClockDuration,
  videoIdFromEntity,
} from 'src/utils/video';
import VideoCardScores from './VideoCardScores';
import VideoCardTitle from './VideoCardTitle';

const useStyles = makeStyles({
  youtube_complements: {
    margin: '4px 0',
    display: 'flex',
    flexWrap: 'wrap',
    alignContent: 'space-between',
    fontFamily: 'Poppins',
    fontStyle: 'italic',
    fontWeight: 'normal',
    fontSize: '0.8em',
    lineHeight: '19px',
    color: '#B6B1A1',
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
  '@keyframes scaling': {
    '0%': {
      opacity: 0.05,
      transform: 'scale(70%)',
    },
    '100%': {
      opacity: 1,
      transform: 'scale(160%)',
    },
  },
  loadingEffect: {
    animation: '1.2s ease-out infinite alternate $scaling',
  },
});

const mainSx = {
  margin: 0,
  width: '100%',
  maxWidth: 1000,
  background: '#FFFFFF',
  border: '1px solid #DCD8CB',
  boxShadow: '0px 0px 8px rgba(0, 0, 0, 0.02), 0px 2px 4px rgba(0, 0, 0, 0.05)',
  borderRadius: '4px',
  alignContent: 'flex-start',
  overflow: 'hidden',
  fontSize: {
    xs: '14px',
    md: '16px',
  },
};

const PlayerWrapper = React.forwardRef(function PlayerWrapper(
  {
    duration,
    children,
  }: {
    duration?: string;
    children: React.ReactNode;
  },
  ref
) {
  const [isDurationVisible, setIsDurationVisible] = useState(true);
  return (
    <Box
      position="relative"
      height="100%"
      onClick={() => setIsDurationVisible(false)}
      ref={ref}
    >
      {isDurationVisible && duration && (
        <Box
          position="absolute"
          bottom={0}
          right={0}
          bgcolor="rgba(0,0,0,0.5)"
          color="#fff"
          px={1}
          fontFamily="system-ui, arial, sans-serif"
          fontSize="0.8em"
          fontWeight="bold"
          sx={{ pointerEvents: 'none' }}
        >
          {duration}
        </Box>
      )}
      {children}
    </Box>
  );
});

const SafeTournesolScoreWrapper = function SafeTournesolScoreWrapper({
  unsafe,
  unsafe_cause,
  children,
}: {
  unsafe: boolean;
  unsafe_cause: string;
  children?: React.ReactNode;
}) {
  const title = (
    <Stack direction="row" alignItems="center" gap={1}>
      <WarningIcon />
      <span>{unsafe_cause}</span>
    </Stack>
  );

  return unsafe ? (
    <Tooltip title={title} placement="right">
      <span>
        <React.Fragment>{children}</React.Fragment>
      </span>
    </Tooltip>
  ) : (
    <React.Fragment>{children}</React.Fragment>
  );
};

function VideoCard({
  video,
  actions = [],
  settings = [],
  compact = false,
}: {
  video: VideoObject;
  actions?: ActionList;
  settings?: ActionList;
  compact?: boolean;
}) {
  const { t, i18n } = useTranslation();
  const theme = useTheme();
  const classes = useStyles();

  const videoId = videoIdFromEntity(video);

  const isSmallScreen = useMediaQuery(theme.breakpoints.down('sm'), {
    noSsr: true,
  });
  const [settingsVisible, setSettingsVisible] = useState(!isSmallScreen);

  return (
    <Grid container spacing={1} sx={mainSx}>
      <Grid
        item
        xs={12}
        sm={compact ? 12 : 'auto'}
        style={{ aspectRatio: '16 / 9', padding: 0, width: '240px' }}
      >
        <ReactPlayer
          url={`https://youtube.com/watch?v=${videoId}`}
          playing
          light
          width="100%"
          height="100%"
          wrapper={PlayerWrapper}
          duration={
            !!video.duration && convertDurationToClockDuration(video.duration)
          }
        />
      </Grid>
      <Grid
        item
        xs={12}
        sm={compact ? 12 : true}
        data-testid="video-card-info"
        container
        direction="column"
      >
        <VideoCardTitle video={video} />
        <div className={classes.youtube_complements}>
          {video.views && (
            <span className={classes.youtube_complements_p}>
              <Trans t={t} i18nKey="video.nbViews">
                {{ nbViews: video.views.toLocaleString(i18n.resolvedLanguage) }}{' '}
                views
              </Trans>
            </span>
          )}
          {video.publication_date && (
            <span className={classes.youtube_complements_p}>
              {video.publication_date}
            </span>
          )}
          {video.uploader && (
            <Tooltip
              title={`${t('video.seeRecommendedVideosSameUploader')}`}
              placement="bottom"
            >
              <Link
                color="inherit"
                component={RouterLink}
                to={`/recommendations?uploader=${encodeURIComponent(
                  video.uploader
                )}`}
              >
                {video.uploader}
              </Link>
            </Tooltip>
          )}
        </div>
        {!compact && <VideoCardScores video={video} />}
      </Grid>
      <Grid
        item
        xs={12}
        sm={compact ? 12 : 1}
        sx={{
          display: 'flex',
          alignItems: 'end',
          flexDirection: 'column',
          padding: '4px !important',
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

export const RowVideoCard = ({ video }: { video: VideoObject }) => {
  const { t, i18n } = useTranslation();
  const classes = useStyles();

  return (
    <Box
      display="flex"
      flexDirection="row"
      alignItems="center"
      gap={1}
      height="70px"
      sx={mainSx}
    >
      <Box sx={{ aspectRatio: '16 / 9', height: '100%' }}>
        <img
          height="100%"
          src={`https://i.ytimg.com/vi/${video.video_id}/mqdefault.jpg`}
        />
      </Box>
      <Box flex={1}>
        <VideoCardTitle video={video} titleMaxLines={1} fontSize="1em" />
        <div className={classes.youtube_complements}>
          {video.views && (
            <span className={classes.youtube_complements_p}>
              <Trans t={t} i18nKey="video.nbViews">
                {{ nbViews: video.views.toLocaleString(i18n.resolvedLanguage) }}{' '}
                views
              </Trans>
            </span>
          )}
          {video.publication_date && (
            <span className={classes.youtube_complements_p}>
              {video.publication_date}
            </span>
          )}
          {video.uploader && (
            <span className={classes.youtube_complements_p}>
              {video.uploader}
            </span>
          )}
        </div>
      </Box>
    </Box>
  );
};

export const VideoCardFromId = ({
  videoId,
  variant = 'full',
  ...rest
}: {
  videoId: string;
  variant: 'full' | 'compact' | 'row';
  [propname: string]: unknown;
}) => {
  const video = useVideoMetadata(videoId);
  if (video == null || !video.video_id) {
    return <EmptyVideoCard compact={variant === 'compact'} />;
  }
  if (variant === 'compact') {
    return <VideoCard video={video} compact {...rest} />;
  }
  if (variant === 'row') {
    return <RowVideoCard video={video} {...rest} />;
  }
  return <VideoCard video={video} {...rest} />;
};

export const EmptyVideoCard = ({
  compact,
  loading = false,
}: {
  compact?: boolean;
  loading?: boolean;
}) => {
  const classes = useStyles();

  return (
    <Grid container spacing={1} sx={mainSx}>
      <Grid
        item
        xs={12}
        sm={compact ? 12 : 4}
        sx={{
          aspectRatio: '16 / 9',
          backgroundColor: '#fafafa',
        }}
        container
        alignItems="center"
        justifyContent="center"
      >
        <img
          src="/svg/LogoSmall.svg"
          alt="logo"
          className={loading ? classes.loadingEffect : undefined}
          style={{ opacity: '0.3' }}
        />
      </Grid>
    </Grid>
  );
};

export default VideoCard;
