import React, { useState, useEffect } from 'react';

import { makeStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import IconButton from '@material-ui/core/IconButton';
import Slider from '@material-ui/core/Slider';
import Button from '@material-ui/core/Button';
import DoubleArrowIcon from '@material-ui/icons/DoubleArrow';
import Grid from '@material-ui/core/Grid';
import Checkbox from '@material-ui/core/Checkbox';

import type { Comparison, ComparisonCriteriaScore } from 'src/services/openapi';
import { handleWikiUrl } from 'src/utils/url';
import { allCriteriaNames } from 'src/utils/constants';

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
  },
  criteriasContainer: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
  },
  sliderContainer: {
    display: 'flex',
    flexDirection: 'row',
    maxWidth: 660,
    width: '100%',
    alignItems: 'center',
  },
  slider: {
    flex: '1 1 0px',
  },
  criteriaNameDisplay: {
    display: 'flex',
    flexDirection: 'row',
    alignItems: 'center',
  },
}));

const ComparisonComponent = ({
  submit,
  initialComparison,
  videoA,
  videoB,
}: {
  submit: (c: Comparison) => void;
  initialComparison: Comparison | null;
  videoA: string;
  videoB: string;
}) => {
  const classes = useStyles();
  const castToComparison = (c: Comparison | null): Comparison => {
    return c
      ? c
      : {
          video_a: { video_id: videoA },
          video_b: { video_id: videoB },
          criteria_scores: [],
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

  const submitComparison = () => {
    setSubmitted(true);
    submit(comparison);
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
        {Object.entries(allCriteriaNames).map(([criteria, criteria_name]) => (
          <div
            key={criteria}
            id={`id_container_criteria_${criteria}`}
            className={classes.criteriasContainer}
          >
            <div className={classes.criteriaNameDisplay}>
              <Grid
                item
                xs={12}
                direction="row"
                justifyContent="center"
                alignItems="center"
                container
              >
                <Typography>
                  <a
                    href={`${handleWikiUrl(
                      window.location.host
                    )}/wiki/Quality_criteria`}
                    id={`id_explanation_${criteria}`}
                    target="_blank"
                    rel="noreferrer"
                  >
                    {criteria_name}{' '}
                    {criteriaValues[criteria] === undefined ? ' (skipped)' : ''}
                  </a>
                </Typography>
                <Checkbox
                  id={`id_checkbox_skip_${criteria}`}
                  disabled={submitted}
                  checked={criteriaValues[criteria] !== undefined}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                    handleSliderChange(
                      criteria,
                      e.target.checked ? 0 : undefined
                    )
                  }
                  color="primary"
                  style={{ padding: 0, marginLeft: 8 }}
                />
              </Grid>
            </div>
            <div className={classes.sliderContainer}>
              <IconButton
                aria-label="left"
                onClick={() => handleSliderChange(criteria, -10)}
                style={{
                  color: 'black',
                  transform: 'rotate(180deg)',
                  padding: 0,
                }}
                disabled={submitted}
              >
                <DoubleArrowIcon />
              </IconButton>
              <Slider
                // ValueLabelComponent={ValueLabelComponent}
                id={`slider_expert_${criteria}`}
                aria-label="custom thumb label"
                color="secondary"
                min={-10}
                step={1}
                max={10}
                value={criteriaValues[criteria] || 0}
                className={classes.slider}
                track={false}
                disabled={submitted || criteriaValues[criteria] === undefined}
                onChange={(
                  _: React.ChangeEvent<unknown>,
                  score: number | number[]
                ) => handleSliderChange(criteria, score as number)}
              />
              <IconButton
                aria-label="right"
                onClick={() => handleSliderChange(criteria, 10)}
                style={{ color: 'black', padding: 0 }}
                disabled={submitted}
              >
                <DoubleArrowIcon />
              </IconButton>
            </div>
          </div>
        ))}
        <div className={classes.criteriasContainer}>
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
        </div>
      </div>
    </div>
  );
};

export default ComparisonComponent;
