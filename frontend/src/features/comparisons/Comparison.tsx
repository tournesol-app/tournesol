import React, { useState, useEffect } from 'react';

import { makeStyles } from '@material-ui/core/styles';
import { Box, Button, Collapse, Typography } from '@material-ui/core';
import ExpandMore from '@material-ui/icons/ExpandMore';
import ExpandLess from '@material-ui/icons/ExpandLess';
import { Info as InfoIcon } from '@material-ui/icons';

import type { Comparison, ComparisonCriteriaScore } from 'src/services/openapi';
import { allCriteriaNames, optionalCriterias } from 'src/utils/constants';

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
  criteriaContainer: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
  },
}));

const ComparisonComponent = ({
  submit,
  initialComparison,
  videoA,
  videoB,
  isComparisonPublic,
}: {
  submit: (c: Comparison) => Promise<void>;
  initialComparison: Comparison | null;
  videoA: string;
  videoB: string;
  isComparisonPublic?: boolean;
}) => {
  const classes = useStyles();
  const castToComparison = (c: Comparison | null): Comparison => {
    return c
      ? c
      : {
          video_a: { video_id: videoA },
          video_b: { video_id: videoB },
          criteria_scores: allCriteriaNames
            .filter(([c]) => !optionalCriterias[c])
            .map(([criteria]) => ({ criteria, score: 0 })),
        };
  };
  const [comparison, setComparison] = useState<Comparison>(
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
    const optionalCriteriaNames = allCriteriaNames.filter(
      ([criteria]) => optionalCriterias[criteria]
    );
    optionalCriteriaNames.forEach(([criteria]) =>
      handleSliderChange(criteria, showOptionalCriterias ? undefined : 0)
    );
  };

  if (videoA == videoB) {
    return (
      <div className={classes.root}>
        <Typography paragraph style={{ textAlign: 'center' }}>
          These two videos are very similar, it is probably not useful to
          compare them. 🌻
        </Typography>
      </div>
    );
  }

  return (
    <div className={classes.root}>
      <div className={classes.centered}>
        {allCriteriaNames
          .filter(([c]) => !optionalCriterias[c])
          .map(([criteria, criteria_name]) => (
            <CriteriaSlider
              key={criteria}
              criteria={criteria}
              criteria_name={criteria_name}
              criteriaValue={criteriaValues[criteria]}
              disabled={submitted}
              handleSliderChange={handleSliderChange}
            />
          ))}
        <Button
          onClick={handleCollapseCriterias}
          startIcon={showOptionalCriterias ? <ExpandLess /> : <ExpandMore />}
          size="small"
          style={{ marginBottom: 8, color: showOptionalCriterias ? 'red' : '' }}
        >
          {showOptionalCriterias
            ? 'Remove optional criterias'
            : 'Add optional criterias'}
        </Button>
        <Collapse
          in={showOptionalCriterias}
          timeout="auto"
          style={{ width: '100%' }}
        >
          {allCriteriaNames
            .filter(([c]) => optionalCriterias[c])
            .map(([criteria, criteria_name]) => (
              <CriteriaSlider
                key={criteria}
                criteria={criteria}
                criteria_name={criteria_name}
                criteriaValue={criteriaValues[criteria]}
                disabled={submitted}
                handleSliderChange={handleSliderChange}
              />
            ))}
        </Collapse>
        {submitted && (
          <div id="id_submitted_text_info">
            <Typography>
              Change one of the video to submit a new comparison
            </Typography>
          </div>
        )}
        <Button
          variant="contained"
          color="primary"
          size="large"
          id="expert_submit_btn"
          onClick={submitted ? () => setSubmitted(false) : submitComparison}
        >
          {submitted ? 'Edit comparison' : 'Submit'}
        </Button>
        {isComparisonPublic && (
          <Box display="flex" alignItems="center" gridGap="8px" m={2}>
            <InfoIcon fontSize="small" color="action" />
            <Typography variant="caption" color="textSecondary">
              {initialComparison
                ? 'This comparison is included in the public dataset.'
                : 'After submission, this comparison will be included in the public dataset.'}
            </Typography>
          </Box>
        )}
      </div>
    </div>
  );
};

export default ComparisonComponent;
