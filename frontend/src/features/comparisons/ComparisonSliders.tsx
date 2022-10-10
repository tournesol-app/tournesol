import React, { useState, useEffect, useRef } from 'react';
import makeStyles from '@mui/styles/makeStyles';
import { Box, Button, Collapse, Typography } from '@mui/material';
import ExpandMore from '@mui/icons-material/ExpandMore';
import ExpandLess from '@mui/icons-material/ExpandLess';
import { Info as InfoIcon } from '@mui/icons-material';
import { useTranslation } from 'react-i18next';

import type {
  ComparisonRequest,
  ComparisonCriteriaScore,
} from 'src/services/openapi';

import CriteriaSlider from './CriteriaSlider';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import { getAllPendingRatings } from 'src/utils/comparison';
import { CriteriaValuesType } from 'src/utils/types';

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
  const { criteriaByName, criterias, active: isPollActive } = useCurrentPoll();

  const isMounted = useRef(true);
  const [disableSubmit, setDisableSubmit] = useState(false);

  const castToComparison = (
    c: ComparisonRequest | null,
    pendingRatings: criteriaValuesType
  ): ComparisonRequest => {
    if (c != null) {
      return c;
    }

    return {
      entity_a: { uid: uidA },
      entity_b: { uid: uidB },
      criteria_scores: criterias
        .filter((c) => !c.optional)
        .map((c) => ({ criteria: c.name, score: pendingRatings[c.name] || 0 })),
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
          getAllPendingRatings(uidA, uidB, criterias, true)
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

    try {
      await submit(comparison);
    } finally {
      setDisableSubmit(false);
    }

    // avoid a "memory leak" warning if the component is unmounted on submit.
    if (isMounted.current) {
      setSubmitted(true);
    }
  };

  const handleSliderChange = (criteria: string, score: number | undefined) => {
    const cs = comparison.criteria_scores.find((c) => c.criteria === criteria);
    if (score === undefined) {
      comparison.criteria_scores = comparison.criteria_scores.filter(
        (c) => c.criteria !== criteria
      );
    } else if (cs) {
      if (cs.score == score) return;
      cs.score = score;
    } else {
      comparison.criteria_scores.push({ criteria, score, weight: 1 });
    }
    setComparison({ ...comparison }); // this is only here to refresh the state
  };

  const showOptionalCriterias = comparison.criteria_scores.some(
    ({ criteria }) => criteriaByName[criteria]?.optional
  );

  const handleCollapseCriterias = () => {
    const optionalCriteriasKeys = criterias
      .filter((c) => c.optional)
      .map((c) => c.name);
    optionalCriteriasKeys.forEach((criteria) =>
      handleSliderChange(criteria, showOptionalCriterias ? undefined : 0)
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
        <Button
          fullWidth
          disabled={!criterias.some((c) => c.optional)}
          onClick={handleCollapseCriterias}
          startIcon={showOptionalCriterias ? <ExpandLess /> : <ExpandMore />}
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
            .filter((c) => c.optional)
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
                  ? t('comparison.comparisonInPublicDataset')
                  : t('comparison.comparisonInPublicDatasetAfterSubmission')}
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
