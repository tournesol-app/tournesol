import React from 'react';

import { useLocation } from 'react-router-dom';
import {
  Grid,
  Typography,
  FormControlLabel,
  Checkbox,
  makeStyles,
} from '@material-ui/core';
import { CheckCircle, CheckCircleOutline } from '@material-ui/icons';

const useStyles = makeStyles(() => ({
  main: {
    display: 'flex',
    flexDirection: 'column',
    paddingLeft: 4,
  },
}));

function DateFilter({
  setFilter,
}: {
  setFilter: (k: string, v: string) => void;
}) {
  const classes = useStyles();
  const Location = useLocation();
  const searchParams = new URLSearchParams(Location.search);

  const dateChoices = ['Today', 'Week', 'Month', 'Year'];
  const date = searchParams.get('date') || 'Any';

  const handleDateChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setFilter('date', event.target.name);
  };

  return (
    <Grid item xs={12} sm={6} md={3}>
      <div className={classes.main}>
        <Typography variant="h5" component="h2">
          Date Uploaded
        </Typography>
        {dateChoices.map((label) => (
          <FormControlLabel
            control={
              <Checkbox
                icon={<CheckCircleOutline />}
                checkedIcon={<CheckCircle />}
                checked={date == label}
                onChange={handleDateChange}
                name={label}
              />
            }
            label={label}
            key={label}
          />
        ))}
      </div>
    </Grid>
  );
}

export default DateFilter;
