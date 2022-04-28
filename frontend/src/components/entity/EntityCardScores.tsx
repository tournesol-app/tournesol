import React from 'react';
import { useTranslation, Trans } from 'react-i18next';
import { Box, Theme, Stack, Tooltip } from '@mui/material';
import { Warning as WarningIcon } from '@mui/icons-material';
import { makeStyles } from '@mui/styles';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import { displayScore } from 'src/utils/criteria';
import { Recommendation } from 'src/services/openapi';
import CriteriaIcon from '../CriteriaIcon';

interface Props {
  entity: Recommendation;
}

/**
 * Criteria excluded from the rated high / low display.
 */
const EXCLUDED_MAIN_CRITERIA = ['largely_recommended', 'be_president'];

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

const EntityCardScores = ({ entity }: Props) => {
  const { t } = useTranslation();
  const classes = useStyles();
  const { getCriteriaLabel } = useCurrentPoll();

  const nbRatings = entity.n_comparisons;
  const nbContributors = entity.n_contributors;

  let max_score = -Infinity;
  let min_score = Infinity;
  let max_criteria = '';
  let min_criteria = '';

  let unsafeCause = '';
  if ('tournesol_score' in entity) {
    if (nbContributors != null && nbContributors <= 1) {
      unsafeCause = t('video.unsafeNotEnoughContributor');
    } else if (entity.tournesol_score && entity.tournesol_score < 0) {
      unsafeCause = t('video.unsafeNegativeRating');
    }
  }
  const isUnsafe = unsafeCause !== '';

  if ('criteria_scores' in entity) {
    entity.criteria_scores?.forEach((criteria) => {
      if (
        criteria.score != undefined &&
        criteria.score > max_score &&
        !EXCLUDED_MAIN_CRITERIA.includes(criteria.criteria)
      ) {
        max_score = criteria.score;
        max_criteria = criteria.criteria;
      }
      if (
        criteria.score != undefined &&
        criteria.score < min_score &&
        !EXCLUDED_MAIN_CRITERIA.includes(criteria.criteria)
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
      {'tournesol_score' in entity && entity.tournesol_score != null && (
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
              {entity.tournesol_score.toFixed(0)}
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
                width="32"
                imgTitle={`${getCriteriaLabel(max_criteria)}: ${displayScore(
                  max_score
                )}`}
              />
            </>
          )}
          <span />
          {min_score < 0 && (
            <>
              <span>{t('video.criteriaRatedLow')}</span>
              <CriteriaIcon
                criteriaName={min_criteria}
                width="32"
                imgTitle={`${getCriteriaLabel(min_criteria)}: ${displayScore(
                  min_score
                )}`}
              />
            </>
          )}
        </Box>
      )}
    </Box>
  );
};

export default EntityCardScores;
