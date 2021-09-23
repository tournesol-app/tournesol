import React from 'react';

import { useLocation } from 'react-router-dom';
import {
  Grid,
  Typography,
  makeStyles,
  withStyles,
  Slider,
  Tooltip,
} from '@material-ui/core';
import { mainCriteriaNames } from 'src/utils/constants';

const useStyles = makeStyles(() => ({
  featuresContainer: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
  },
  sliderContainer: {
    display: 'flex',
    flexDirection: 'row',
    width: 'calc(100% - 64px)',
    alignItems: 'center',
    margin: '-2px',
  },
  featureNameDisplay: {
    display: 'flex',
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  criteria_img: {
    marginRight: 4,
  },
  valueText: {
    margin: 4,
  },
}));

const CustomSlider = withStyles({
  root: {
    color: '#1282B2',
    height: 2,
    padding: '15px 0',
  },
  active: {},
  track: {
    height: 2,
  },
  rail: {
    height: 2,
    opacity: 0.5,
    backgroundColor: '#bfbfbf',
  },
  mark: {
    backgroundColor: '#bfbfbf',
    height: 8,
    width: 1,
    marginTop: -3,
  },
  markActive: {
    opacity: 1,
    backgroundColor: 'currentColor',
  },
})(Slider);

function CriteriaFilter({
  setFilter,
}: {
  setFilter: (k: string, v: string) => void;
}) {
  const classes = useStyles();
  const Location = useLocation();
  const searchParams = new URLSearchParams(Location.search);
  const marks = [0, 25, 50, 75, 100].map((value) => ({ value }));

  function valuetoText(value: number) {
    if (value == 0) {
      return 'Ignore';
    } else if (value == 25) {
      return 'Not important';
    } else if (value == 50) {
      return 'Neutral';
    } else if (value == 75) {
      return 'Important';
    } else {
      return 'Crucial';
    }
  }

  interface Props {
    children: React.ReactElement;
    open: boolean;
    value: number;
  }

  function ValueLabelComponent(props: Props) {
    const { children, open, value } = props;
    return (
      <Tooltip open={open} enterTouchDelay={0} placement="top" title={value}>
        {children}
      </Tooltip>
    );
  }

  return (
    <Grid item xs={12} sm={12} md={6}>
      <Typography variant="h5" component="h2">
        Criteria
      </Typography>
      <Grid container>
        {Object.entries(mainCriteriaNames).map(([feature, feature_name]) => (
          <Grid item xs={12} sm={6} key={feature}>
            <div
              id={`id_container_feature_${feature}`}
              className={classes.featuresContainer}
            >
              <div className={classes.featureNameDisplay}>
                <Grid
                  item
                  xs={12}
                  direction="row"
                  justifyContent="center"
                  alignItems="center"
                  container
                >
                  <img
                    className={classes.criteria_img}
                    src={`/svg/${feature}.svg`}
                  />
                  <Typography>
                    <span>{feature_name}</span>
                  </Typography>
                </Grid>
              </div>
              <div className={classes.sliderContainer}>
                <Grid
                  item
                  xs={6}
                  direction="row"
                  justifyContent="flex-start"
                  alignItems="flex-start"
                  container
                >
                  <span className={classes.valueText}>
                    {valuetoText(parseInt(searchParams.get(feature) || '50'))}
                  </span>
                </Grid>
                <Grid
                  item
                  xs={12}
                  direction="row"
                  justifyContent="flex-start"
                  alignItems="flex-start"
                  container
                >
                  <CustomSlider
                    name={feature}
                    defaultValue={parseInt(searchParams.get(feature) || '50')}
                    step={25}
                    min={0}
                    max={100}
                    valueLabelDisplay="auto"
                    valueLabelFormat={valuetoText}
                    onChangeCommitted={(e, value) =>
                      setFilter(feature, value.toString())
                    }
                    ValueLabelComponent={ValueLabelComponent}
                    marks={marks}
                  />
                </Grid>
              </div>
            </div>
          </Grid>
        ))}
      </Grid>
    </Grid>
  );
}

export default CriteriaFilter;
