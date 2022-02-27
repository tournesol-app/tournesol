import React from 'react';
import { useTranslation } from 'react-i18next';

import makeStyles from '@mui/styles/makeStyles';
import Typography from '@mui/material/Typography';
import Slider from '@mui/material/Slider';
import Grid from '@mui/material/Grid';
import Checkbox from '@mui/material/Checkbox';

import { getWikiBaseUrl } from 'src/utils/url';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';

const SLIDER_MIN_STEP = -10;
const SLIDER_MAX_STEP = 10;
const SLIDER_STEP = 1;

const useStyles = makeStyles(() => ({
  criteriaContainer: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
  },
  sliderContainer: {
    display: 'flex',
    flexDirection: 'row',
    maxWidth: 660,
    width: 'calc(100% - 64px)',
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
  img_criteria: {
    padding: 4,
  },
}));

const CriteriaSlider = ({
  criteria,
  criteriaLabel,
  criteriaValue,
  disabled,
  handleSliderChange,
}: {
  criteria: string;
  criteriaLabel: string;
  criteriaValue: number | undefined;
  disabled: boolean;
  handleSliderChange: (criteria: string, value: number | undefined) => void;
}) => {
  const { t } = useTranslation();
  const classes = useStyles();
  const { criteriaByName } = useCurrentPoll();

  const computeMedian = function (
    min: number,
    max: number,
    step: number
  ): number {
    return (max - min) / (2 * step);
  };

  const neutralPos = computeMedian(
    SLIDER_MIN_STEP,
    SLIDER_MAX_STEP,
    SLIDER_STEP
  );

  return (
    <div
      id={`id_container_criteria_${criteria}`}
      className={classes.criteriaContainer}
      style={{ width: '100%' }}
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
          {criteria != 'largely_recommended' && (
            <img
              className={classes.img_criteria}
              src={`/svg/${criteria}.svg`}
            />
          )}
          <Typography>
            <a
              href={`${getWikiBaseUrl()}/wiki/Quality_criteria`}
              id={`id_explanation_${criteria}`}
              target="_blank"
              rel="noreferrer"
            >
              {criteriaLabel}{' '}
              {criteriaValue === undefined
                ? `(${t('comparison.criteriaSkipped')})`
                : ''}
            </a>
          </Typography>
          {(criteriaByName[criteria]?.optional ||
            criteriaValue == undefined) && (
            <Checkbox
              id={`id_checkbox_skip_${criteria}`}
              disabled={disabled}
              checked={criteriaValue !== undefined}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                handleSliderChange(criteria, e.target.checked ? 0 : undefined)
              }
              color="primary"
              sx={{
                padding: 0,
                marginLeft: '8px',
              }}
            />
          )}
        </Grid>
      </div>
      <div className={classes.sliderContainer}>
        <Slider
          sx={{
            [`& span[data-index="${neutralPos}"].MuiSlider-mark`]: {
              height: '12px',
            },
          }}
          id={`slider_expert_${criteria}`}
          aria-label="custom thumb label"
          color="secondary"
          min={SLIDER_MIN_STEP}
          max={SLIDER_MAX_STEP}
          step={SLIDER_STEP}
          marks
          value={criteriaValue || 0}
          className={classes.slider}
          track={false}
          disabled={disabled || criteriaValue === undefined}
          onChange={(_: Event, score: number | number[]) =>
            handleSliderChange(criteria, score as number)
          }
        />
      </div>
    </div>
  );
};

export default CriteriaSlider;
