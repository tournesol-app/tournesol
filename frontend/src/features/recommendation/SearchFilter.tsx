import React, { useState } from 'react';
import { Collapse, Grid, Box, Badge } from '@mui/material';

import makeStyles from '@mui/styles/makeStyles';

import { CollapseButton } from 'src/components';
import { useListFilter } from 'src/hooks';
import LanguageFilter from './LanguageFilter';
import DateFilter from './DateFilter';
import CriteriaFilter from './CriteriaFilter';
import UploaderFilter from './UploaderFilter';
import { recommendationFilters } from 'src/utils/constants';

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

  const isFilterActive = () => {
    for (const pair of filterParams.entries()) {
      if (pair[0] in recommendationFilters && parseInt(pair[1], 10) !== 50) {
        return true;
      }
    }
    return false;
  };

  return (
    <Box color="text.secondary">
      <Badge color="secondary" variant="dot" invisible={!isFilterActive()}>
        <CollapseButton expanded={expanded} onClick={handleExpandClick} />
      </Badge>
      <Collapse in={expanded} timeout="auto" unmountOnExit>
        {filterParams.get(recommendationFilters.uploader) && (
          <Box marginBottom={1}>
            <UploaderFilter
              value={filterParams.get(recommendationFilters.uploader) ?? ''}
              onDelete={() => setFilter(recommendationFilters.uploader, '')}
            />
          </Box>
        )}
        <Grid container spacing={4} className={classes.filtersContainer}>
          <Grid item xs={6} md={3} lg={2} data-testid="search-date-filter">
            <DateFilter
              value={filterParams.get(recommendationFilters.date) ?? ''}
              onChange={(value) => setFilter(recommendationFilters.date, value)}
            />
          </Grid>
          <Grid item xs={6} md={3} lg={2} data-testid="search-language-filter">
            <LanguageFilter
              value={filterParams.get(recommendationFilters.language) ?? ''}
              onChange={(value) =>
                setFilter(recommendationFilters.language, value)
              }
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
