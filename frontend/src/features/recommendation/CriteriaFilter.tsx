import React, { useState } from 'react';
import { useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Grid, Typography, Slider, Tooltip } from '@mui/material';
//import Autocomplete from '@mui/material/Autocomplete';

import makeStyles from '@mui/styles/makeStyles';
import withStyles from '@mui/styles/withStyles';

import { TitledSection, CriteriaIcon } from 'src/components';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import CriteriaSelector from 'src/features/criteria/CriteriaSelector';
import FormGroup from '@mui/material/FormGroup';
import FormControlLabel from '@mui/material/FormControlLabel';
import Switch from '@mui/material/Switch';

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

interface ValueLabelProps {
  children: React.ReactElement;
  open: boolean;
  value: number;
}

interface FilterProps {
  setFilter: (k: string, v: string) => void;
}

function ValueLabelComponent(props: ValueLabelProps) {
  const { children, open, value } = props;
  return (
    <Tooltip open={open} enterTouchDelay={0} placement="top" title={value}>
      {children}
    </Tooltip>
  );
}

function SingleCriteriaFilter({ setFilter }: FilterProps) {
  const { criterias } = useCurrentPoll();
  const [selectedCriteria, setSelectedCriteria] = useState(criterias[0].name);

  function handleCriteriaChange(criteria: string) {
    setSelectedCriteria(criteria);
    criterias.forEach((c) => setFilter(c.name, '0'));
    setFilter(criteria, '100');
  }

  return (
    <CriteriaSelector
      criteria={selectedCriteria}
      setCriteria={handleCriteriaChange}
    />
  );
}

function MultipleCriteriaFilter({ setFilter }: FilterProps) {
  const { t } = useTranslation();
  const classes = useStyles();
  const Location = useLocation();
  const searchParams = new URLSearchParams(Location.search);
  const marks = [0, 25, 50, 75, 100].map((value) => ({ value }));
  const { criterias } = useCurrentPoll();

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
    <Grid container spacing={1}>
      {criterias.map((criteria) => {
        const criteriaLabel = criteria.label;
        return (
          <Grid item xs={12} sm={6} key={criteria.name}>
            <div
              id={`id_container_feature_${criteria.name}`}
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
                  <CriteriaIcon
                    criteriaName={criteria.name}
                    sx={{
                      marginRight: '6px',
                    }}
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
                    <span title={criteriaLabel}>{criteriaLabel}</span>
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
                      parseInt(searchParams.get(criteria.name) || '50')
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
                    name={criteria.name}
                    defaultValue={parseInt(
                      searchParams.get(criteria.name) || '50'
                    )}
                    step={25}
                    min={0}
                    max={100}
                    size="small"
                    valueLabelDisplay="auto"
                    valueLabelFormat={valuetoText}
                    onChangeCommitted={(e, value) =>
                      setFilter(criteria.name, value.toString())
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
  );
}

function CriteriaFilter({ setFilter }: FilterProps) {
  const [isMultipleFilter, setIsMultipleFilter] = useState(false);
  const { t } = useTranslation();
  return (
    <>
      <TitledSection title={t('filter.criteria')}>
        <FormGroup>
          <FormControlLabel
            control={
              <Switch
                checked={isMultipleFilter}
                onChange={() => setIsMultipleFilter(!isMultipleFilter)}
              />
            }
            label={t('filter.multipleCriteria') as string}
            aria-label="multiple criteria"
          />
        </FormGroup>
        {isMultipleFilter ? (
          <MultipleCriteriaFilter setFilter={setFilter} />
        ) : (
          <SingleCriteriaFilter setFilter={setFilter} />
        )}
      </TitledSection>
    </>
  );
}

export default CriteriaFilter;
