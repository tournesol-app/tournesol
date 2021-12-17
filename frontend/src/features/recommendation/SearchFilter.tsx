import React, { useState } from 'react';
import { Collapse, Grid, Box } from '@mui/material';

import makeStyles from '@mui/styles/makeStyles';

import { CollapseButton } from 'src/components';
import { useListFilter } from 'src/hooks';
import LanguageFilter from './LanguageFilter';
import DateFilter from './DateFilter';
import CriteriaFilter from './CriteriaFilter';
import UploaderFilter from './UploaderFilter';

const useStyles = makeStyles({
  filtersContainer: {
    marginBottom: '8px',
  },
});

function SearchFilter() {
  const classes = useStyles();
  const [expanded, setExpanded] = useState(false);
  const [filterParams, setFilter] = useListFilter();

  const handleExpandClick = () => {
    setExpanded(!expanded);
  };

  return (
    <Box color="text.secondary">
      <CollapseButton expanded={expanded} onClick={handleExpandClick} />
      <Collapse in={expanded} timeout="auto" unmountOnExit>
        {searchParams.get('uploader') && (
          <UploaderFilter
            value={searchParams.get('uploader') ?? ''}
            onDelete={() => setFilter('uploader', '')}
          />
        )}
        <Grid container spacing={4} className={classes.filtersContainer}>
          <Grid item xs={6} md={3} lg={2}>
            <DateFilter
              value={filterParams.get('date') ?? ''}
              onChange={(value) => setFilter('date', value)}
            />
          </Grid>
          <Grid item xs={6} md={3} lg={2}>
            <LanguageFilter
              value={filterParams.get('language') ?? ''}
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
