import React, { useState } from 'react';
import { useLocation, useHistory } from 'react-router-dom';

import { makeStyles, Collapse, Button, Grid } from '@material-ui/core';
import { ExpandLess, ExpandMore } from '@material-ui/icons';
import LanguageFilter from './LanguageFilter';
import DateFilter from './DateFilter';
import CriteriaFilter from './CriteriaFilter';

const useStyles = makeStyles(() => ({
  filter: {
    color: '#506AD4',
    margin: '8px',
  },
  collapse: {
    display: 'flex',
    flexWrap: 'wrap',
    alignContent: 'space-between',
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
    if (searchParams.get(key) === value) {
      searchParams.delete(key);
    } else {
      searchParams.delete(key);
      searchParams.append(key, value);
    }
    history.push('/recommendations/?' + searchParams.toString());
  }

  return (
    <div className="filters">
      <Button
        color="secondary"
        size="large"
        className={classes.filter}
        startIcon={!expanded ? <ExpandMore /> : <ExpandLess />}
        aria-expanded={expanded}
        aria-label="show more"
        onClick={handleExpandClick}
      >
        Filters
      </Button>
      <Collapse
        className={classes.collapse}
        in={expanded}
        timeout="auto"
        unmountOnExit
      >
        <Grid container>
          <CriteriaFilter setFilter={setFilter} />
          <DateFilter setFilter={setFilter} />
          <LanguageFilter setFilter={setFilter} />
        </Grid>
      </Collapse>
    </div>
  );
}

export default SearchFilter;
