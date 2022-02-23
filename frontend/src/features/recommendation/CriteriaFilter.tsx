import React from 'react';
import { useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Grid, Typography, Slider, Tooltip } from '@mui/material';

import makeStyles from '@mui/styles/makeStyles';
import withStyles from '@mui/styles/withStyles';

import { mainCriterias, getCriteriaName } from 'src/utils/constants';
import { TitledSection } from 'src/components';

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
  const { t } = useTranslation();
  const classes = useStyles();
  const Location = useLocation();
  const searchParams = new URLSearchParams(Location.search);
  const marks = [0, 25, 50, 75, 100].map((value) => ({ value }));

  function valuetoText(value: number) {
    if (value == 0) {
      return t('filter.ignore');
    } else if (value == 25) {
      return t('filter.notImportant');
    } else if (value == 50) {
      return t('filter.neutral');
    } else if (value == 75) {
      return t('filter.important');
    } else {
      return t('filter.crucial');
    }
  }

  return (
    <TitledSection title={t('filter.criteria')}>
      <Grid container spacing={1}>
        {mainCriterias.map((criteria) => {
          const criteriaName = getCriteriaName(t, criteria);
          return (
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
                    <Typography
                      sx={{
                        flex: 1,
                        fontSize: '0.85rem',
                        whiteSpace: 'nowrap',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                      }}
                    >
                      <span title={criteriaName}>{criteriaName}</span>
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
                    <Typography
                      sx={{
                        maxWidth: 'calc(100% - 8px)',
                        margin: '2px !important',
                        fontSize: '0.7rem',
                        fontWeight: 600,
                        whiteSpace: 'nowrap',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                      }}
                    >
                      {valuetoText(
                        parseInt(searchParams.get(criteria) || '50')
                      )}
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
                      defaultValue={parseInt(
                        searchParams.get(criteria) || '50'
                      )}
                      step={25}
                      min={0}
                      max={100}
                      size="small"
                      valueLabelDisplay="auto"
                      valueLabelFormat={valuetoText}
                      onChangeCommitted={(e, value) =>
                        setFilter(criteria, value.toString())
                      }
                      components={{
                        ValueLabel: ValueLabelComponent,
                      }}
                      marks={marks}
                    />
                  </Grid>
                </div>
              </div>
            </Grid>
          );
        })}
      </Grid>
    </TitledSection>
  );
}

export default CriteriaFilter;
