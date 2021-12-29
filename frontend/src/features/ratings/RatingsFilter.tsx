import React, { useState } from 'react';
import { Collapse, Grid, Box } from '@mui/material';

import { CollapseButton } from 'src/components';
import { useListFilter } from 'src/hooks';
import IsPublicFilter from './IsPublicFilter';
import MarkAllRatingsMenu from './MarkAllRatings';

function RatingsFilter() {
  const [expanded, setExpanded] = useState(false);
  const [filterParams, setFilter] = useListFilter();

  const handleExpandClick = () => {
    setExpanded(!expanded);
  };

  return (
    <Box color="text.secondary">
      <CollapseButton expanded={expanded} onClick={handleExpandClick}>
        Options
      </CollapseButton>
      <Collapse in={expanded} timeout="auto" unmountOnExit>
        <Grid container spacing={4} style={{ marginBottom: '8px' }}>
          <Grid item xs={12} sm={6} md={4}>
            <IsPublicFilter
              value={filterParams.get('isPublic') ?? ''}
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
