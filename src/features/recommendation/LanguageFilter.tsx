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

function LanguageFilter({
  setFilter,
}: {
  setFilter: (k: string, v: string) => void;
}) {
  const classes = useStyles();
  const Location = useLocation();
  const searchParams = new URLSearchParams(Location.search);
  const language = searchParams.get('language') || '';

  const languageChoices = {
    en: 'English',
    fr: 'French',
    de: 'German',
  };

  const handleLanguageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setFilter('language', event.target.name);
  };

  return (
    <Grid item xs={12} sm={6} md={3}>
      <div className={classes.main}>
        <Typography variant="h5" component="h2">
          Language
        </Typography>
        {Object.entries(languageChoices).map(
          ([language_key, language_value]) => (
            <FormControlLabel
              control={
                <Checkbox
                  icon={<CheckCircleOutline />}
                  checkedIcon={<CheckCircle />}
                  checked={language == language_key}
                  onChange={handleLanguageChange}
                  name={language_key}
                />
              }
              label={language_value}
              key={language_key}
            />
          )
        )}
      </div>
    </Grid>
  );
}

export default LanguageFilter;
