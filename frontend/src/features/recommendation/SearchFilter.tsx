import React, { useState } from 'react';
import { useLocation, useHistory } from 'react-router-dom';

import { Collapse, Button, Grid, Box, Theme } from '@material-ui/core';
import { useTheme } from '@material-ui/styles';

import { ExpandLess, ExpandMore } from '@material-ui/icons';
import LanguageFilter from './LanguageFilter';
import DateFilter from './DateFilter';
import CriteriaFilter from './CriteriaFilter';

function SearchFilter() {
  const theme: Theme = useTheme();
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
        style={{
          padding: '8px 0',
          color: expanded
            ? theme.palette.secondary.main
            : theme.palette.action.active,
        }}
      >
        Filters
      </Button>
      <Collapse in={expanded} timeout="auto" unmountOnExit>
        <Grid container spacing={4} style={{ marginBottom: '8px' }}>
          <Grid item xs={12} sm={6} md={3}>
            <DateFilter
              value={searchParams.get('date') ?? ''}
              onChange={(value) => setFilter('date', value)}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
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
