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
import { FilterSection } from 'src/components/filter/FilterSection';

const useStyles = makeStyles(() => ({
  featuresContainer: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'left',
    margin: '2px 0px',
  },
  sliderContainer: {
    display: 'flex',
    flexDirection: 'row',
    width: '100%',
    alignItems: 'center',
    margin: '-2px',
  },
  featureNameDisplay: {
    display: 'flex',
    flexDirection: 'row',
    alignItems: 'center',
  },
  criteria_img: {
    marginRight: 6,
  },
  criteriaName: {
    flex: 1,
    fontSize: '0.85rem',
    whiteSpace: 'nowrap',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
  },
  valueText: {
    maxWidth: 'calc(100% - 8px)',
    margin: 2,
    fontSize: '0.7rem',
    fontWeight: 600,
    whiteSpace: 'nowrap',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
  },
}));

const CustomSlider = withStyles({
  root: {
    color: '#1282B2',
  },
  active: {},
  rail: {
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

  return (
    <FilterSection title="Criteria">
      <Grid container spacing={1}>
        {mainCriteriaNames.map(([criteria, criteria_name]) => (
          <Grid item xs={12} sm={6} key={criteria}>
            <div
              id={`id_container_feature_${criteria}`}
              className={classes.featuresContainer}
            >
              <div className={classes.featureNameDisplay}>
                <Grid
                  item
                  xs={12}
                  direction="row"
                  justifyContent="flex-start"
                  alignItems="center"
                  container
                >
                  <img
                    className={classes.criteria_img}
                    src={`/svg/${criteria}.svg`}
                    width="16px"
                  />
                  <Typography className={classes.criteriaName}>
                    <span title={criteria_name}>{criteria_name}</span>
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
                  <Typography className={classes.valueText}>
                    {valuetoText(parseInt(searchParams.get(criteria) || '50'))}
                  </Typography>
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
                    name={criteria}
                    defaultValue={parseInt(searchParams.get(criteria) || '50')}
                    step={25}
                    min={0}
                    max={100}
                    valueLabelDisplay="auto"
                    valueLabelFormat={valuetoText}
                    onChangeCommitted={(e, value) =>
                      setFilter(criteria, value.toString())
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
    </FilterSection>
  );
}

export default CriteriaFilter;
