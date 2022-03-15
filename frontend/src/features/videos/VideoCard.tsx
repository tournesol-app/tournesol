import React, { useState } from 'react';
import ReactPlayer from 'react-player/youtube';
import { useTranslation } from 'react-i18next';
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
import EntityCardTitle from 'src/components/entity/EntityCardTitle';
import { entityCardMainSx } from 'src/components/entity/style';
import EmptyEntityCard from 'src/components/entity/EmptyEntityCard';
import { PlayerWrapper } from 'src/components/entity/EntityImagery';
import { VideoMetadata } from 'src/components/entity/EntityMetadata';

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
  controls = true,
}: {
  video: VideoObject;
  actions?: ActionList;
  settings?: ActionList;
  compact?: boolean;
  controls?: boolean;
}) {
  const { t } = useTranslation();
  const theme = useTheme();
  const classes = useStyles();

  const videoId = videoIdFromEntity(video);

  const isSmallScreen = useMediaQuery(theme.breakpoints.down('sm'), {
    noSsr: true,
  });
  const [settingsVisible, setSettingsVisible] = useState(!isSmallScreen);

  return (
    <Grid container sx={entityCardMainSx}>
      <Grid
        item
        xs={12}
        sm={compact ? 12 : 'auto'}
        sx={{ aspectRatio: '16 / 9', width: '240px !important' }}
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
          controls={controls}
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
        <EntityCardTitle title={video.name} compact={compact} />
        <VideoMetadata
          views={video.views}
          publicationDate={video.publication_date}
          uploader={video.uploader}
        />
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
  return (
    <Box
      display="flex"
      flexDirection="row"
      alignItems="center"
      gap={1}
      height="70px"
      sx={entityCardMainSx}
    >
      <Box sx={{ aspectRatio: '16 / 9', height: '100%' }}>
        <img
          height="100%"
          src={`https://i.ytimg.com/vi/${video.video_id}/mqdefault.jpg`}
        />
      </Box>
      <Box flex={1}>
        <EntityCardTitle title={video.name} titleMaxLines={1} fontSize="1em" />
        <VideoMetadata
          views={video.views}
          uploader={video.uploader}
          publicationDate={video.publication_date}
          withLinks={false}
        />
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
    return <EmptyEntityCard compact={variant === 'compact'} />;
  }
  if (variant === 'compact') {
    return <VideoCard video={video} compact {...rest} />;
  }
  if (variant === 'row') {
    return <RowVideoCard video={video} {...rest} />;
  }
  return <VideoCard video={video} {...rest} />;
};

export default VideoCard;
