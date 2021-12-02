/* eslint-disable react/no-unescaped-entities */
import React, { useState } from 'react';
import ReactPlayer from 'react-player/youtube';
import clsx from 'clsx';

import { makeStyles } from '@material-ui/core/styles';
import {
  Typography,
  Grid,
  Box,
  Collapse,
  IconButton,
  useMediaQuery,
  useTheme,
} from '@material-ui/core';

import { mainCriteriaNamesObj } from 'src/utils/constants';
import { ActionList, VideoObject } from 'src/utils/types';
import { useVideoMetadata } from './VideoApi';
import {
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
} from '@material-ui/icons';

const useStyles = makeStyles((theme) => ({
  main: {
    maxWidth: 1000,
    background: '#FFFFFF',
    border: '1px solid #DCD8CB',
    boxShadow:
      '0px 0px 8px rgba(0, 0, 0, 0.02), 0px 2px 4px rgba(0, 0, 0, 0.05)',
    borderRadius: '4px',
    alignContent: 'flex-start',
    overflow: 'hidden',
    fontSize: '16px',
    [theme.breakpoints.down('xs')]: {
      fontSize: '14px',
    },
  },
  title: {
    fontFamily: 'Poppins',
    // Limit text to 3 lines and show ellipsis
    display: '-webkit-box',
    overflow: 'hidden',
    '-webkit-line-clamp': 3,
    '-webkit-box-orient': 'vertical',
  },
  title_compact: {
    fontSize: '1em',
  },
  youtube_complements: {
    margin: 4,
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
  channel: {
    textDecorationLine: 'underline',
  },
  nb_tournesol: {
    fontFamily: 'Poppins',
    fontStyle: 'normal',
    fontWeight: 'bold',
    fontSize: '2em',
    lineHeight: '32px',
  },
  ratings: {
    marginRight: '4px',
    fontFamily: 'Poppins',
    fontStyle: 'italic',
    fontWeight: 'normal',
    fontSize: '0.9em',
    color: '#A09B87',
  },
  contributors: {
    fontFamily: 'Poppins',
    fontStyle: 'italic',
    fontWeight: 500,
    fontSize: '0.9em',
    textDecorationLine: 'underline',
    color: '#B38B00',
  },
  rated: {
    fontFamily: 'Poppins',
    fontStyle: 'normal',
    fontWeight: 'normal',
    fontSize: '0.9em',
    color: '#847F6E',
    gap: '8px',
  },
  top: {
    display: 'flex',
    flexWrap: 'wrap',
    alignContent: 'space-between',
  },
  actionsContainer: {
    display: 'flex',
    alignItems: 'end',
    flexDirection: 'column',
    [theme.breakpoints.down('xs')]: {
      flexDirection: 'row',
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
}));

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
  const theme = useTheme();
  const classes = useStyles();
  const videoId = video.video_id;
  let total_score = 0;
  let max_score = -Infinity;
  let min_score = Infinity;
  let max_criteria = '';
  let min_criteria = '';

  const isSmallScreen = useMediaQuery(theme.breakpoints.down('xs'), {
    noSsr: true,
  });
  const [settingsVisible, setSettingsVisible] = useState(!isSmallScreen);

  if ('criteria_scores' in video) {
    video.criteria_scores?.forEach((criteria) => {
      total_score += criteria.score != undefined ? 10 * criteria.score : 0;
      if (
        criteria.score != undefined &&
        criteria.score > max_score &&
        criteria.criteria != 'largely_recommended'
      ) {
        max_score = criteria.score;
        max_criteria = criteria.criteria;
      }
      if (
        criteria.score != undefined &&
        criteria.score < min_score &&
        criteria.criteria != 'largely_recommended'
      ) {
        min_score = criteria.score;
        min_criteria = criteria.criteria;
      }
    });
  }

  return (
    <Grid container spacing={1} className={classes.main}>
      <Grid
        item
        xs={12}
        sm={compact ? 12 : 4}
        style={{ aspectRatio: '16 / 9', padding: 0 }}
      >
        <ReactPlayer
          url={`https://youtube.com/watch?v=${videoId}`}
          playing
          light
          width="100%"
          height="100%"
        />
      </Grid>
      <Grid
        item
        xs={12}
        sm={compact ? 12 : 7}
        data-testid="video-card-info"
        container
        direction="column"
      >
        <div className={classes.top}>
          <Typography
            className={clsx(classes.title, {
              [classes.title_compact]: compact,
            })}
            variant={compact ? 'inherit' : 'h5'}
            title={video.name}
          >
            {video.name}
          </Typography>
        </div>
        <div className={classes.youtube_complements}>
          {video.views && (
            <span className={classes.youtube_complements_p}>
              {video.views} views
            </span>
          )}
          {video.publication_date && (
            <span className={classes.youtube_complements_p}>
              {video.publication_date}
            </span>
          )}
          {video.uploader && (
            <span className={classes.channel}>{video.uploader}</span>
          )}
        </div>
        {!compact && (
          <Box
            display="flex"
            flexWrap="wrap"
            alignItems="center"
            style={{ gap: '12px' }}
          >
            {'criteria_scores' in video && (
              <Box
                display="flex"
                alignItems="center"
                data-testid="video-card-overall-score"
              >
                <img
                  className="tournesol"
                  src={'/svg/tournesol.svg'}
                  alt="logo"
                  title="Overall score"
                  width={32}
                />
                <span className={classes.nb_tournesol}>
                  {total_score.toFixed(0)}
                </span>
              </Box>
            )}

            {!!video.rating_n_ratings && video.rating_n_ratings > 0 && (
              <Box data-testid="video-card-ratings">
                <span className={classes.ratings}>
                  {video.rating_n_ratings} comparisons by{' '}
                </span>
                <span className={classes.contributors}>
                  {video.rating_n_contributors} contributors
                </span>
              </Box>
            )}

            {max_criteria !== '' && min_criteria !== max_criteria && (
              <Box
                data-testid="video-card-minmax-criterias"
                display="flex"
                alignItems="center"
                className={classes.rated}
              >
                <span>Rated high:</span>
                <img
                  src={`/svg/${max_criteria}.svg`}
                  alt={max_criteria}
                  title={mainCriteriaNamesObj[max_criteria]}
                />
                <span>Rated low:</span>
                <img
                  src={`/svg/${min_criteria}.svg`}
                  alt={min_criteria}
                  title={mainCriteriaNamesObj[min_criteria]}
                />
              </Box>
            )}
          </Box>
        )}
      </Grid>
      <Grid
        item
        xs={12}
        sm={compact ? 12 : 1}
        className={classes.actionsContainer}
      >
        {actions.map((Action, index) =>
          typeof Action === 'function' ? (
            <Action key={index} videoId={videoId} />
          ) : (
            Action
          )
        )}
        {isSmallScreen && settings.length > 0 && (
          <>
            <Box flexGrow={1} />
            <IconButton
              size="small"
              aria-label="Show settings related to this video"
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
              gridGap="16px"
              color="text.secondary"
            >
              {settings.map((Action, index) =>
                typeof Action === 'function' ? (
                  <Action key={index} videoId={videoId} />
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

export const VideoCardFromId = ({
  videoId,
  compact,
}: {
  videoId: string;
  compact?: boolean;
}) => {
  const video = useVideoMetadata(videoId);
  if (video == null || !video.video_id) {
    return <EmptyVideoCard compact={compact} />;
  }
  return <VideoCard video={video} compact={compact} />;
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
    <Grid container spacing={1} className={classes.main}>
      <Grid
        item
        xs={12}
        sm={compact ? 12 : 4}
        style={{
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
