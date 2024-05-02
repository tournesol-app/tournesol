import React, { useState, useEffect, useRef, useContext } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';

import makeStyles from '@mui/styles/makeStyles';
import { Box, Button, Collapse, Typography } from '@mui/material';
import ExpandMore from '@mui/icons-material/ExpandMore';
import ExpandLess from '@mui/icons-material/ExpandLess';
import { Info as InfoIcon } from '@mui/icons-material';

import type {
  ComparisonRequest,
  ComparisonCriteriaScore,
  PollCriteria,
} from 'src/services/openapi';
import { selectSettings } from 'src/features/settings/userSettingsSlice';
import StatsContext from 'src/features/statistics/StatsContext';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import {
  clearPendingRating,
  getAllPendingRatings,
  resetPendingRatings,
} from 'src/utils/comparison/pending';
import { CriteriaValuesType } from 'src/utils/types';
import CriteriaSlider, { SLIDER_SCORE_MAX } from './CriteriaSlider';

const useStyles = makeStyles(() => ({
  root: {
    width: '100%',
    display: 'flex',
    justifyContent: 'center',
  },
  centered: {
    flex: '0 0 auto',
    maxWidth: 660,
    width: 'calc(100% - 64px)',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
  },
}));

/**
 * A criterion can be considered "collapsed" if:
 *  - it is configured optional in the poll
 *  - the user haven't marked it as always displayed
 */
const isCollapsed = (
  criterion: PollCriteria | undefined,
  userPreferences: string[] | undefined
) => {
  return criterion?.optional && !userPreferences?.includes(criterion.name);
};

const ComparisonSliders = ({
  submit,
  initialComparison,
  uidA,
  uidB,
  isComparisonPublic,
}: {
  submit: (c: ComparisonRequest) => Promise<void>;
  initialComparison: ComparisonRequest | null;
  uidA: string;
  uidB: string;
  isComparisonPublic?: boolean;
}) => {
  const classes = useStyles();
  const { t } = useTranslation();

  const {
    criteriaByName,
    criterias,
    name: pollName,
    active: isPollActive,
  } = useCurrentPoll();

  const { refreshStats } = useContext(StatsContext);

  const userSettings = useSelector(selectSettings)?.settings;
  const critAlwaysDisplayed = userSettings.videos?.comparison__criteria_order;

  const isMounted = useRef(true);
  const [disableSubmit, setDisableSubmit] = useState(false);

  const castToComparison = (
    c: ComparisonRequest | null,
    pendingRatings: CriteriaValuesType
  ): ComparisonRequest => {
    if (c != null) {
      return c;
    }

    return {
      entity_a: { uid: uidA },
      entity_b: { uid: uidB },
      criteria_scores: criterias
        .filter((c) => !c.optional || critAlwaysDisplayed?.includes(c.name))
        .map((c) => ({
          criteria: c.name,
          score: pendingRatings[c.name] || 0,
          score_max: SLIDER_SCORE_MAX,
        })),
    };
  };

  const [comparison, setComparison] = useState<ComparisonRequest>(
    castToComparison(initialComparison, {})
  );
  const [submitted, setSubmitted] = useState(false);

  const criteriaValues: CriteriaValuesType = {};
  comparison.criteria_scores.forEach((cs: ComparisonCriteriaScore) => {
    criteriaValues[cs.criteria] = cs.score || 0;
  });

  /**
   * If `initialComparison` is set, initialize the sliders with the provided
   * ratings, else create a new comparison.
   *
   * If pending ratings are detected for the couple uidA / uidB, the new
   * comparison is initialized with them.
   */
  useEffect(
    () => {
      setComparison(
        castToComparison(
          initialComparison,
          getAllPendingRatings(pollName, uidA, uidB, criterias)
        )
      );
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [initialComparison]
  );

  useEffect(() => {
    // the cleanup function will be called when the component is unmounted
    return () => {
      isMounted.current = false;
    };
  }, []);

  const submitComparison = async () => {
    setDisableSubmit(true);
    resetPendingRatings();

    try {
      await submit(comparison);
    } finally {
      setDisableSubmit(false);
      refreshStats(pollName);
    }

    // avoid a "memory leak" warning if the component is unmounted on submit.
    if (isMounted.current) {
      setSubmitted(true);
    }
  };

  const handleSliderChange = (
    criteria: string,
    score: number | undefined,
    scoreMax: number
  ) => {
    const cs = comparison.criteria_scores.find((c) => c.criteria === criteria);
    if (score === undefined) {
      comparison.criteria_scores = comparison.criteria_scores.filter(
        (c) => c.criteria !== criteria
      );
    } else if (cs) {
      if (cs.score == score) return;
      cs.score = score;
      cs.score_max = scoreMax;
    } else {
      comparison.criteria_scores.push({
        criteria,
        score,
        score_max: scoreMax,
        weight: 1,
      });
    }

    clearPendingRating(pollName, uidA, uidB, criteria);
    setComparison({ ...comparison }); // this is only here to refresh the state
  };

  const showOptionalCriterias = comparison.criteria_scores.some(
    ({ criteria }) => isCollapsed(criteriaByName[criteria], critAlwaysDisplayed)
  );

  const handleCollapseCriterias = () => {
    const optionalCriteriasKeys = criterias
      .filter((c) => isCollapsed(c, critAlwaysDisplayed))
      .map((c) => c.name);

    optionalCriteriasKeys.forEach((criteria) =>
      handleSliderChange(
        criteria,
        showOptionalCriterias ? undefined : 0,
        SLIDER_SCORE_MAX
      )
    );
  };

  if (uidA == uidB) {
    return (
      <div className={classes.root}>
        <Typography sx={{ textAlign: 'center' }}>
          {t('comparison.itemsAreSimilar')}
          {' 🌻'}
        </Typography>
      </div>
    );
  }

  return (
    <div className={classes.root}>
      <div className={classes.centered}>
        {criterias
          .filter((c) => !c.optional)
          .map((criteria) => (
            <CriteriaSlider
              key={criteria.name}
              criteria={criteria.name}
              criteriaLabel={criteria.label}
              criteriaValue={criteriaValues[criteria.name]}
              disabled={submitted}
              handleSliderChange={handleSliderChange}
            />
          ))}

        {critAlwaysDisplayed != undefined &&
          critAlwaysDisplayed
            .filter(
              (criteria) => criterias.find((c) => c.name === criteria)?.optional
            )
            .map((criterionName) => (
              <CriteriaSlider
                key={criterionName}
                criteria={criterionName}
                criteriaLabel={
                  criterias.find((c) => c.name === criterionName)?.label ??
                  criterionName
                }
                criteriaValue={criteriaValues[criterionName]}
                disabled={submitted}
                handleSliderChange={handleSliderChange}
              />
            ))}

        {!criterias
          .filter((c) => c.optional)
          .every((optCriterion) => {
            return critAlwaysDisplayed?.includes(optCriterion.name);
          }) && (
          <>
            <Button
              fullWidth
              disabled={
                !criterias.some((c) => isCollapsed(c, critAlwaysDisplayed))
              }
              onClick={handleCollapseCriterias}
              startIcon={
                showOptionalCriterias ? <ExpandLess /> : <ExpandMore />
              }
              size="medium"
              color="secondary"
              sx={{
                marginBottom: '8px',
                color: showOptionalCriterias ? 'red' : '',
              }}
            >
              {showOptionalCriterias
                ? t('comparison.removeOptionalCriterias')
                : t('comparison.addOptionalCriterias')}
            </Button>

            <Collapse
              in={showOptionalCriterias}
              timeout="auto"
              sx={{ width: '100%' }}
            >
              {criterias
                .filter((c) => isCollapsed(c, critAlwaysDisplayed))
                .map((criteria) => (
                  <CriteriaSlider
                    key={criteria.name}
                    criteria={criteria.name}
                    criteriaLabel={criteria.label}
                    criteriaValue={criteriaValues[criteria.name]}
                    disabled={submitted}
                    handleSliderChange={handleSliderChange}
                  />
                ))}
            </Collapse>
          </>
        )}

        {submitted && (
          <div id="id_submitted_text_info">
            <Typography>{t('comparison.changeOneItem')}</Typography>
          </div>
        )}

        <Box
          display="flex"
          alignItems="center"
          gap="8px"
          my={1}
          color="text.hint"
          minHeight="40px"
        >
          {isComparisonPublic && (
            <>
              <InfoIcon fontSize="small" color="inherit" />
              <Typography variant="caption" color="textSecondary">
                {initialComparison
                  ? t('comparison.comparisonInPublicData')
                  : t('comparison.comparisonInPublicDataAfterSubmission')}
              </Typography>
            </>
          )}
        </Box>
        <Button
          disabled={disableSubmit || !isPollActive}
          variant="contained"
          color="primary"
          size="large"
          id="expert_submit_btn"
          onClick={submitted ? () => setSubmitted(false) : submitComparison}
        >
          {submitted ? t('comparison.editComparison') : t('submit')}
        </Button>
      </div>
    </div>
  );
};

export default ComparisonSliders;
