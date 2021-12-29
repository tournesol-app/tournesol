import React from 'react';

import makeStyles from '@mui/styles/makeStyles';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import Slider from '@mui/material/Slider';
import Grid from '@mui/material/Grid';
import Checkbox from '@mui/material/Checkbox';
import DoubleArrowIcon from '@mui/icons-material/DoubleArrow';

import { handleWikiUrl } from 'src/utils/url';
import { optionalCriterias } from 'src/utils/constants';

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
  img_criteria: {
    padding: 4,
  },
}));

const CriteriaSlider = ({
  criteria,
  criteria_name,
  criteriaValue,
  disabled,
  handleSliderChange,
}: {
  criteria: string;
  criteria_name: string;
  criteriaValue: number | undefined;
  disabled: boolean;
  handleSliderChange: (criteria: string, value: number | undefined) => void;
}) => {
  const classes = useStyles();

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
              href={`${handleWikiUrl(
                window.location.host
              )}/wiki/Quality_criteria`}
              id={`id_explanation_${criteria}`}
              target="_blank"
              rel="noreferrer"
            >
              {criteria_name} {criteriaValue === undefined ? ' (skipped)' : ''}
            </a>
          </Typography>
          {(optionalCriterias[criteria] || criteriaValue == undefined) && (
            <Checkbox
              id={`id_checkbox_skip_${criteria}`}
              disabled={disabled}
              checked={criteriaValue !== undefined}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                handleSliderChange(criteria, e.target.checked ? 0 : undefined)
              }
              color="primary"
              style={{ padding: 0, marginLeft: 8 }}
            />
          )}
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
          disabled={disabled}
          size="large">
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
          value={criteriaValue || 0}
          className={classes.slider}
          track={false}
          disabled={disabled || criteriaValue === undefined}
          onChange={(_: React.ChangeEvent<unknown>, score: number | number[]) =>
            handleSliderChange(criteria, score as number)
          }
        />
        <IconButton
          aria-label="right"
          onClick={() => handleSliderChange(criteria, 10)}
          style={{ color: 'black', padding: 0 }}
          disabled={disabled}
          size="large">
          <DoubleArrowIcon />
        </IconButton>
      </div>
    </div>
  );
};

export default CriteriaSlider;
