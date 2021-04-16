import React from 'react';

import { makeStyles, withStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import Slider from '@material-ui/core/Slider';
// import Button from '@material-ui/core/Button';
// import Grid from '@material-ui/core/Grid';
import Box from '@material-ui/core/Box';

import Tooltip from '@material-ui/core/Tooltip';
import { featureNames, featureColors } from '../../constants';

const sliderMarks = {
  0: 'Ignore',
  25: 'Somewhat important',
  50: 'Important',
  80: 'Crucial',
};

function closestLabel(val, marks) {
  // https://stackoverflow.com/questions/8584902/get-the-closest-number-out-of-an-array
  const closestIdx = Object.keys(marks).reduce(
    (prev, curr) => (Math.abs(curr - val) < Math.abs(prev - val) ? curr : prev),
  );
  return marks[closestIdx];
}

const useStyles = makeStyles(() => ({
  sliderContainer: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    marginTop: '4px',
  },
}));

const TournesolSlider = withStyles({
  root: {
    width: 'calc(100% - 8px)',
  },
  thumb: {
    transition: 'left 1s',
  },
  track: {
    transition: 'width 1s',
  },
  active: {
    transition: 'left 0s',
  },
})(Slider);

export default ({ preferences, setPreferences }) => {
  const classes = useStyles();

  // THE COMMENTED OUT CODE IS THREE BTTONS ALLOWING TO SET
  // THE VALUE OF THE PREFERENCE TO 0%, 50% or 100%

  // const setAll = (val) => {
  //   const newPrefs = { ...preferences };
  //   Object.keys(preferences).forEach((key) => {
  //     newPrefs[key] = val;
  //   });
  //   setPreferences(newPrefs);
  // };

  return (
    <>
      {Object.keys(preferences).map((feature) => (
        <Box
          width="100%"
          borderColor={featureColors[feature]}
          border={3}
          borderRadius={5}
          className={classes.sliderContainer}
        >
          <Typography
            gutterBottom
            style={{ width: '100%', marginBottom: '-4px' }}
            align="center"
          >
            {featureNames[feature] || feature}
          </Typography>
          <Tooltip
            title={closestLabel(preferences[feature], sliderMarks)}
            aria-label="add"
          >
            <TournesolSlider
              aria-label="custom thumb label"
              color="secondary"
              value={preferences[feature]}
              id={`preference_slider_${feature}`}
              onChange={(e, value) => {
                setPreferences({ ...preferences, [feature]: value });
              }}
            />
          </Tooltip>
        </Box>
      ))}
      {/* <Grid container item xs={12} spacing={3}>
        <Grid item xs={3}>
          Set all
        </Grid>
        <Grid item xs={3}>
          <Button
            variant="contained"
            color="primary"
            onClick={() => setAll(0)}
            style={{ marginBottom: '8px', fontSize: '8px' }}
          >
            do not care
          </Button>
        </Grid>

        <Grid item xs={3}>
          <Button
            variant="contained"
            color="primary"
            onClick={() => setAll(50)}
            style={{ marginBottom: '8px', fontSize: '8px' }}
          >
            care a bit
          </Button>
        </Grid>

        <Grid item xs={3}>
          <Button
            variant="contained"
            color="primary"
            onClick={() => setAll(100)}
            style={{ marginBottom: '8px', fontSize: '8px' }}
          >
            care a lot
          </Button>
        </Grid>
      </Grid> */}
    </>
  );
};
