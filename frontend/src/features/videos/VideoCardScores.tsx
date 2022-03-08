import React from 'react';
import { useTranslation, Trans } from 'react-i18next';
import { Box, Theme, Stack, Tooltip } from '@mui/material';
import { Warning as WarningIcon } from '@mui/icons-material';
import { VideoObject } from 'src/utils/types';
import { makeStyles } from '@mui/styles';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';

interface Props {
  video: VideoObject;
}

const useStyles = makeStyles((theme: Theme) => ({
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
}));

const VideoCardScores = ({ video }: Props) => {
  const { t } = useTranslation();
  const classes = useStyles();
  const { getCriteriaLabel } = useCurrentPoll();

  const nbRatings = video.rating_n_ratings;
  const nbContributors = video.rating_n_contributors;

  let max_score = -Infinity;
  let min_score = Infinity;
  let max_criteria = '';
  let min_criteria = '';

  let unsafeCause = '';
  if ('tournesol_score' in video) {
    if (nbContributors != null && nbContributors <= 1) {
      unsafeCause = t('video.unsafeNotEnoughContributor');
    } else if (video.tournesol_score && video.tournesol_score < 0) {
      unsafeCause = t('video.unsafeNegativeRating');
    }
  }
  const isUnsafe = unsafeCause !== '';

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

  const tournesolScoreTitle = isUnsafe ? (
    <Stack direction="row" alignItems="center" gap={1}>
      <WarningIcon />
      <span>{unsafeCause}</span>
    </Stack>
  ) : (
    ''
  );

  return (
    <Box
      display="flex"
      flexWrap="wrap"
      alignItems="center"
      columnGap="12px"
      paddingBottom={1}
    >
      {'tournesol_score' in video && video.tournesol_score != null && (
        <Tooltip title={tournesolScoreTitle} placement="right">
          <Box
            display="flex"
            alignItems="center"
            data-testid="video-card-overall-score"
            {...(isUnsafe && {
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
              {video.tournesol_score.toFixed(0)}
            </span>
          </Box>
        </Tooltip>
      )}

      {nbRatings != null && nbRatings > 0 && (
        <Box data-testid="video-card-ratings">
          <span className={classes.ratings}>
            <Trans t={t} i18nKey="video.nbComparisonsBy" count={nbRatings}>
              {{ count: nbRatings }} comparisons by
            </Trans>
          </span>{' '}
          <span className={classes.contributors}>
            <Trans t={t} i18nKey="video.nbContributors" count={nbContributors}>
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
            fontSize: '0.9em',
            color: 'text.secondary',
            gap: '6px',
          }}
        >
          <span>{t('video.criteriaRatedHigh')}</span>
          <img
            src={`/svg/${max_criteria}.svg`}
            alt={max_criteria}
            title={getCriteriaLabel(max_criteria)}
          />
          <span />
          <span>{t('video.criteriaRatedLow')}</span>
          <img
            src={`/svg/${min_criteria}.svg`}
            alt={min_criteria}
            title={getCriteriaLabel(min_criteria)}
          />
        </Box>
      )}
    </Box>
  );
};

export default VideoCardScores;
