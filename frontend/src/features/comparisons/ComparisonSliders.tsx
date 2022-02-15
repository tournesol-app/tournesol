import React, { useState, useEffect } from 'react';
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
import {
  allCriterias,
  optionalCriterias,
  getCriteriaName,
} from 'src/utils/constants';

import CriteriaSlider from './CriteriaSlider';

const useStyles = makeStyles(() => ({
  root: {
    width: '100%',
    display: 'flex',
    justifyContent: 'center',
    overflow: 'hidden',
  },
  centered: {
    paddingBottom: '32px',
    width: '880px',
    flex: '0 0 auto',
    maxWidth: '100%',

    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
  },
}));

const ComparisonSliders = ({
  submit,
  initialComparison,
  videoA,
  videoB,
  isComparisonPublic,
}: {
  submit: (c: ComparisonRequest) => Promise<void>;
  initialComparison: ComparisonRequest | null;
  videoA: string;
  videoB: string;
  isComparisonPublic?: boolean;
}) => {
  const { t } = useTranslation();
  const classes = useStyles();
  const castToComparison = (c: ComparisonRequest | null): ComparisonRequest => {
    return c
      ? c
      : {
          entity_a: { video_id: videoA },
          entity_b: { video_id: videoB },
          criteria_scores: allCriterias
            .filter((c) => !optionalCriterias[c])
            .map((criteria) => ({ criteria, score: 0 })),
        };
  };
  const [comparison, setComparison] = useState<ComparisonRequest>(
    castToComparison(initialComparison)
  );
  const [submitted, setSubmitted] = useState(false);

  type criteriaValuesType = { [s: string]: number | undefined };
  const criteriaValues: criteriaValuesType = {};
  comparison.criteria_scores.forEach((cs: ComparisonCriteriaScore) => {
    criteriaValues[cs.criteria] = cs.score || 0;
  });

  useEffect(
    () => setComparison(castToComparison(initialComparison)),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [initialComparison]
  );

  const submitComparison = async () => {
    await submit(comparison);
    setSubmitted(true);
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
    ({ criteria }) => optionalCriterias[criteria]
  );

  const handleCollapseCriterias = () => {
    const optionalCriteriasKeys = allCriterias.filter(
      (criteria) => optionalCriterias[criteria]
    );
    optionalCriteriasKeys.forEach((criteria) =>
      handleSliderChange(criteria, showOptionalCriterias ? undefined : 0)
    );
  };

  if (videoA == videoB) {
    return (
      <div className={classes.root}>
        <Typography paragraph style={{ textAlign: 'center' }}>
          {t('comparison.videosAreSimilar')}
          {' 🌻'}
        </Typography>
      </div>
    );
  }

  return (
    <div className={classes.root}>
      <div className={classes.centered}>
        {allCriterias
          .filter((c) => !optionalCriterias[c])
          .map((criteria) => (
            <CriteriaSlider
              key={criteria}
              criteria={criteria}
              criteria_name={getCriteriaName(t, criteria)}
              criteriaValue={criteriaValues[criteria]}
              disabled={submitted}
              handleSliderChange={handleSliderChange}
            />
          ))}
        <Button
          onClick={handleCollapseCriterias}
          startIcon={showOptionalCriterias ? <ExpandLess /> : <ExpandMore />}
          size="small"
          color="secondary"
          style={{ marginBottom: 8, color: showOptionalCriterias ? 'red' : '' }}
        >
          {showOptionalCriterias
            ? t('comparison.removeOptionalCriterias')
            : t('comparison.addOptionalCriterias')}
        </Button>
        <Collapse
          in={showOptionalCriterias}
          timeout="auto"
          style={{ width: '100%' }}
        >
          {allCriterias
            .filter((c) => optionalCriterias[c])
            .map((criteria) => (
              <CriteriaSlider
                key={criteria}
                criteria={criteria}
                criteria_name={getCriteriaName(t, criteria)}
                criteriaValue={criteriaValues[criteria]}
                disabled={submitted}
                handleSliderChange={handleSliderChange}
              />
            ))}
        </Collapse>
        {submitted && (
          <div id="id_submitted_text_info">
            <Typography>{t('comparison.changeOneVideo')}</Typography>
          </div>
        )}
        <Button
          variant="contained"
          color="primary"
          size="large"
          id="expert_submit_btn"
          onClick={submitted ? () => setSubmitted(false) : submitComparison}
        >
          {submitted ? t('comparison.editComparison') : t('submit')}
        </Button>
        {isComparisonPublic && (
          <Box
            display="flex"
            alignItems="center"
            gap="8px"
            m={2}
            color="text.hint"
          >
            <InfoIcon fontSize="small" color="inherit" />
            <Typography variant="caption" color="textSecondary">
              {initialComparison
                ? t('comparison.comparisonInPublicDataset')
                : t('comparison.comparisonInPublicDatasetAfterSubmission')}
            </Typography>
          </Box>
        )}
      </div>
    </div>
  );
};

export default ComparisonSliders;
