import React from 'react';
import { useTranslation, Trans } from 'react-i18next';
import { Box, Theme } from '@mui/system';
import { VideoObject } from 'src/utils/types';
import { makeStyles } from '@mui/styles';
import { getCriteriaName } from 'src/utils/constants';

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
  rated: {
    fontFamily: 'Poppins',
    fontStyle: 'normal',
    fontWeight: 'normal',
    fontSize: '0.9em',
    color: '#847F6E',
    gap: '8px',
  },
}));

const VideoCardScores = ({ video }: Props) => {
  const { t } = useTranslation();
  const classes = useStyles();

  const nbRatings = video.rating_n_ratings;
  const nbContributors = video.rating_n_contributors;

  let total_score = 0;
  let max_score = -Infinity;
  let min_score = Infinity;
  let max_criteria = '';
  let min_criteria = '';

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
    <Box
      display="flex"
      flexWrap="wrap"
      alignItems="center"
      columnGap="12px"
      paddingBottom={1}
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
          <span className={classes.nb_tournesol}>{total_score.toFixed(0)}</span>
        </Box>
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
          className={classes.rated}
        >
          <span>{t('video.criteriaRatedHigh')}</span>
          <img
            src={`/svg/${max_criteria}.svg`}
            alt={max_criteria}
            title={getCriteriaName(t, max_criteria)}
          />
          <span>{t('video.criteriaRatedLow')}</span>
          <img
            src={`/svg/${min_criteria}.svg`}
            alt={min_criteria}
            title={getCriteriaName(t, min_criteria)}
          />
        </Box>
      )}
    </Box>
  );
};

export default VideoCardScores;
