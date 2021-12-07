import React, { useState } from 'react';
import { useLocation, useHistory } from 'react-router-dom';
import { Collapse, Grid, Box, makeStyles } from '@material-ui/core';

import { FiltersButton } from 'src/components';
import LanguageFilter from './LanguageFilter';
import DateFilter from './DateFilter';
import CriteriaFilter from './CriteriaFilter';

const useStyles = makeStyles({
  filtersContainer: {
    marginBottom: '8px',
  },
});

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
      <FiltersButton expanded={expanded} onClick={handleExpandClick} />
      <Collapse in={expanded} timeout="auto" unmountOnExit>
        <Grid container spacing={4} className={classes.filtersContainer}>
          <Grid item xs={6} md={3} lg={2}>
            <DateFilter
              value={searchParams.get('date') ?? ''}
              onChange={(value) => setFilter('date', value)}
            />
          </Grid>
          <Grid item xs={6} md={3} lg={2}>
            <LanguageFilter
              value={searchParams.get('language') ?? ''}
              onChange={(value) => setFilter('language', value)}
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
