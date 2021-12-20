import React, { useState } from 'react';
import { useLocation, useHistory } from 'react-router-dom';
import clsx from 'clsx';

import { Collapse, Button, Grid, Box, Theme } from '@material-ui/core';
import { makeStyles } from '@material-ui/styles';

import { ExpandLess, ExpandMore } from '@material-ui/icons';
import LanguagesFilter from './LanguagesFilter';
import DateFilter from './DateFilter';
import CriteriaFilter from './CriteriaFilter';

const useStyles = makeStyles((theme: Theme) => ({
  filtersButton: {
    padding: '8px 0',
  },
  filtersButtonDefault: {
    color: theme.palette.action.active,
  },
  filtersButtonExpanded: {
    color: theme.palette.secondary.main,
  },
  filtersContainer: {
    marginBottom: '8px',
  },
}));

function SearchFilter() {
  const classes = useStyles();
  const [expanded, setExpanded] = useState(false);
  const Location = useLocation();
  const history = useHistory();
  const searchParams = new URLSearchParams(Location.search);

  const handleExpandClick = () => {
    setExpanded(!expanded);
  };

  function setFilter(key: string, value: string) {
    if (value) {
      searchParams.set(key, value);
    } else {
      searchParams.delete(key);
    }
    // Reset pagination if filters change
    if (key !== 'offset') {
      searchParams.delete('offset');
    }
    history.push({ search: searchParams.toString() });
  }

  return (
    <Box color="text.secondary">
      <Button
        size="large"
        startIcon={!expanded ? <ExpandMore /> : <ExpandLess />}
        aria-expanded={expanded}
        aria-label="show more"
        onClick={handleExpandClick}
        className={clsx(classes.filtersButton, {
          [classes.filtersButtonDefault]: !expanded,
          [classes.filtersButtonExpanded]: expanded,
        })}
      >
        Filters
      </Button>
      <Collapse in={expanded} timeout="auto" unmountOnExit>
        <Grid container spacing={4} className={classes.filtersContainer}>
          <Grid item xs={6} md={3} lg={2}>
            <DateFilter
              value={searchParams.get('date') ?? ''}
              onChange={(value) => setFilter('date', value)}
            />
          </Grid>
          <Grid item xs={6} md={3} lg={2}>
            <LanguagesFilter
              value={searchParams.get('languages') ?? ''}
              onChange={(value) => setFilter('languages', value)}
            />
          </Grid>
          <Grid item xs={12} sm={12} md={6}>
            <CriteriaFilter setFilter={setFilter} />
          </Grid>
        </Grid>
      </Collapse>
    </Box>
  );
}

export default SearchFilter;
