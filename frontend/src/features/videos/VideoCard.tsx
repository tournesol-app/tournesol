import React, { useState } from 'react';
import ReactPlayer from 'react-player/youtube';
import { Link as RouterLink } from 'react-router-dom';
import { useTranslation, Trans } from 'react-i18next';
import makeStyles from '@mui/styles/makeStyles';
import {
  Typography,
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
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';

const useStyles = makeStyles((theme) => ({
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
    color: theme.palette.neutral.main,
  },
  contributors: {
    fontFamily: 'Poppins',
    fontStyle: 'italic',
    fontWeight: 500,
    fontSize: '0.9em',
    color: '#B38B00',
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
}));

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
      // Use spread operator to work around missing typing for 'ref' in MUI `Box`
      // See https://github.com/mui-org/material-ui/issues/17010
      {...{ ref }}
    >
      {isDurationVisible && duration && (
        <Box
          position="absolute"
          bottom={0}
          right={0}
          bgcolor="rgba(0,0,0,0.5)"
          color="#fff"
          px={1}
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
  const { getCriteriaLabel } = useCurrentPoll();

  const videoId = videoIdFromEntity(video);
  const tournesolScore = video.tournesol_score;

  let max_score = -Infinity;
  let min_score = Infinity;
  let max_criteria = '';
  let min_criteria = '';
  let unsafe = false;
  let unsafe_cause = '';

  const isSmallScreen = useMediaQuery(theme.breakpoints.down('sm'), {
    noSsr: true,
  });
  const [settingsVisible, setSettingsVisible] = useState(!isSmallScreen);

  if ('criteria_scores' in video) {
    video.criteria_scores?.forEach((criteria) => {
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

  const nbRatings = video.rating_n_ratings;
  const nbContributors = video.rating_n_contributors;
  if (nbContributors != null && nbContributors <= 1) {
    unsafe = true;
    unsafe_cause = t('video.unsafeNotEnoughContributor');
  }
  if (tournesolScore && tournesolScore < 0) {
    unsafe = true;
    unsafe_cause = t('video.unsafeNegativeRating');
  }

  return (
    <Grid container spacing={1} sx={mainSx}>
      <Grid
        item
        xs={12}
        sm={compact ? 12 : 4}
        sx={{ aspectRatio: '16 / 9', padding: '0 !important' }}
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
        sm={compact ? 12 : 7}
        data-testid="video-card-info"
        container
        direction="column"
      >
        <div className={classes.top}>
          <Typography
            sx={{
              fontFamily: 'Poppins',
              textAlign: 'left',
              // Limit text to 3 lines and show ellipsis
              display: '-webkit-box',
              overflow: 'hidden',
              WebkitLineClamp: 3,
              WebkitBoxOrient: 'vertical',
              fontSize: compact ? '1em !important' : '',
            }}
            variant={compact ? 'inherit' : 'h5'}
            title={video.name}
          >
            {video.name}
          </Typography>
        </div>
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
          <Tooltip
            title={`${t('video.seeRecommendedVideosSameUploader')}`}
            placement="bottom"
          >
            <div>
              {video.uploader && (
                <Link
                  color="inherit"
                  component={RouterLink}
                  to={`/recommendations?uploader=${encodeURIComponent(
                    video.uploader
                  )}`}
                >
                  {video.uploader}
                </Link>
              )}
            </div>
          </Tooltip>
        </div>
        {!compact && (
          <Box
            display="flex"
            flexWrap="wrap"
            alignItems="center"
            sx={{ gap: '12px' }}
          >
            {tournesolScore && (
              <SafeTournesolScoreWrapper
                unsafe={unsafe}
                unsafe_cause={unsafe_cause}
              >
                <Box
                  display="flex"
                  alignItems="center"
                  data-testid="video-card-overall-score"
                  {...(unsafe == true && {
                    sx: {
                      filter: 'grayscale(100%)',
                      opacity: 0.6,
                    },
                  })}
                >
                  <img
                    className="tournesol"
                    src={'/svg/tournesol.svg'}
                    alt="logo"
                    title="Overall score"
                    width={32}
                  />
                  <span className={classes.nb_tournesol}>
                    {tournesolScore.toFixed(0)}
                  </span>
                </Box>
              </SafeTournesolScoreWrapper>
            )}

            {nbRatings != null && nbRatings > 0 && (
              <Box data-testid="video-card-ratings">
                <span className={classes.ratings}>
                  <Trans
                    t={t}
                    i18nKey="video.nbComparisonsBy"
                    count={nbRatings}
                  >
                    {{ count: nbRatings }} comparisons by
                  </Trans>
                </span>{' '}
                <span className={classes.contributors}>
                  <Trans
                    t={t}
                    i18nKey="video.nbContributors"
                    count={nbContributors}
                  >
                    {{ count: nbContributors }} contributors
                  </Trans>
                </span>
              </Box>
            )}

            {max_criteria !== '' && min_criteria !== max_criteria && (
              <Box
                data-testid="video-card-minmax-criterias"
                display="flex"
                alignItems="center"
                sx={{
                  fontFamily: 'Poppins',
                  fontStyle: 'normal',
                  fontWeight: 'normal',
                  fontSize: '0.9em',
                  color: '#847F6E',
                  gap: '8px',
                }}
              >
                <span>{t('video.criteriaRatedHigh')}</span>
                <img
                  src={`/svg/${max_criteria}.svg`}
                  alt={max_criteria}
                  title={getCriteriaLabel(max_criteria)}
                />
                <span>{t('video.criteriaRatedLow')}</span>
                <img
                  src={`/svg/${min_criteria}.svg`}
                  alt={min_criteria}
                  title={getCriteriaLabel(min_criteria)}
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
