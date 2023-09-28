import React from 'react';
import { useTranslation, Trans } from 'react-i18next';
import { Box, Theme, Stack, Tooltip, Typography } from '@mui/material';
import {
  Warning as WarningIcon,
  HelpOutline as HelpIcon,
} from '@mui/icons-material';
import { makeStyles } from '@mui/styles';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import CriteriaIcon from '../CriteriaIcon';
import { EntityResult } from 'src/utils/types';

interface Props {
  result: EntityResult;
  showTournesolScore?: boolean;
  showTotalScore?: boolean;
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

const EntityCardScores = ({
  result,
  showTournesolScore = true,
  showTotalScore = false,
}: Props) => {
  const { t } = useTranslation();
  const classes = useStyles();
  const { getCriteriaLabel, options } = useCurrentPoll();
  const mainCriterionName = options?.mainCriterionName ?? '';

  if (!('collective_rating' in result) || result.collective_rating == null) {
    return null;
  }

  const nbRatings = result.collective_rating.n_comparisons;
  const nbContributors = result.collective_rating.n_contributors;

  let max_score = -Infinity;
  let min_score = Infinity;
  let max_criteria = '';
  let min_criteria = '';

  const isUnsafe = result.collective_rating.unsafe.status;
  const unsafeReasons = result.collective_rating.unsafe.reasons
    .map((reason) => {
      if (reason === 'insufficient_tournesol_score') {
        return t('video.insufficientScore');
      }
      if (reason === 'insufficient_trust') {
        return t('video.unsafeNotEnoughContributor');
      }
      return '';
    })
    .filter((str) => str !== '');

  if ('criteria_scores' in result.collective_rating) {
    result.collective_rating.criteria_scores.forEach((criteria) => {
      if (
        criteria.score != undefined &&
        criteria.score > max_score &&
        mainCriterionName !== criteria.criteria
      ) {
        max_score = criteria.score;
        max_criteria = criteria.criteria;
      }
      if (
        criteria.score != undefined &&
        criteria.score < min_score &&
        mainCriterionName !== criteria.criteria
      ) {
        min_score = criteria.score;
        min_criteria = criteria.criteria;
      }
    });
  }

  const tournesolScoreTitle =
    isUnsafe && unsafeReasons.length > 0 ? (
      <Stack direction="row" alignItems="center" gap={1}>
        <WarningIcon />
        <Box display="flex" flexDirection="column" gap={1}>
          {unsafeReasons.map((reason) => (
            <span key={reason}>{reason}</span>
          ))}
        </Box>
      </Stack>
    ) : (
      ''
    );

  const totalScore =
    'recommendation_metadata' in result
      ? result.recommendation_metadata.total_score
      : null;

  return (
    <>
      {showTotalScore && totalScore != null && (
        <Box display="flex" alignItems="center" columnGap={1}>
          <Typography color="text.secondary">
            Score : <strong>{totalScore.toFixed(2)}</strong>
            {''}
          </Typography>
          <Tooltip
            title={t('score.totalScoreBasedOnRankingChoice')}
            placement="right"
          >
            <HelpIcon fontSize="inherit" color="action" />
          </Tooltip>
        </Box>
      )}
      <Box
        display="flex"
        flexWrap="wrap"
        alignItems="center"
        columnGap="12px"
        py={1}
      >
        {showTournesolScore &&
          result.collective_rating?.tournesol_score != null && (
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
                  {result.collective_rating.tournesol_score.toFixed(0)}
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

        {max_criteria !== '' && (
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
            {max_score > 0 && (
              <>
                <span>{t('video.criteriaRatedHigh')}</span>
                <CriteriaIcon
                  criteriaName={max_criteria}
                  emojiSize="26px"
                  imgWidth="32px"
                  tooltip={`${getCriteriaLabel(
                    max_criteria
                  )}: ${max_score.toFixed(0)}`}
                />
              </>
            )}
            <span />
            {min_score < 0 && (
              <>
                <span>{t('video.criteriaRatedLow')}</span>
                <CriteriaIcon
                  criteriaName={min_criteria}
                  emojiSize="26px"
                  imgWidth="32px"
                  tooltip={`${getCriteriaLabel(
                    min_criteria
                  )}: ${min_score.toFixed(0)}`}
                />
              </>
            )}
          </Box>
        )}
      </Box>
    </>
  );
};

export default EntityCardScores;
