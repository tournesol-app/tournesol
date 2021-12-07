import React, { useState } from 'react';
import { useLocation, useHistory } from 'react-router-dom';

import { Collapse, Grid, Box } from '@material-ui/core';

import { FiltersButton } from 'src/components';
import IsPublicFilter from './IsPublicFilter';
import MarkAllRatingsMenu from './MarkAllRatings';

function RatingsFilter() {
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
      <FiltersButton expanded={expanded} onClick={handleExpandClick}>
        Options
      </FiltersButton>
      <Collapse in={expanded} timeout="auto" unmountOnExit>
        <Grid container spacing={4} style={{ marginBottom: '8px' }}>
          <Grid item xs={12} sm={6} md={4}>
            <IsPublicFilter
              value={searchParams.get('isPublic') ?? ''}
              onChange={(value) => setFilter('isPublic', value)}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <MarkAllRatingsMenu />
          </Grid>
        </Grid>
      </Collapse>
    </Box>
  );
}

export default RatingsFilter;
