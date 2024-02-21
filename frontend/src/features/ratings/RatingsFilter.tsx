import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Box, Collapse, Grid } from '@mui/material';

import { CollapseButton } from 'src/components';
import { useListFilter } from 'src/hooks';

import IsPublicFilter from './IsPublicFilter';
import MarkAllRatingsMenu from './MarkAllRatings';
import RatingOrderByInput from './RatingOrderByInput';

function RatingsFilter({
  defaultFilters = [],
  onAllRatingsChange,
}: {
  // A list of default values used to initialize the filters.
  defaultFilters: Array<{ name: string; value: string }>;
  onAllRatingsChange: () => void;
}) {
  const { t } = useTranslation();
  const [expanded, setExpanded] = useState(false);
  const [filterParams, setFilter] = useListFilter({ defaults: defaultFilters });

  const handleExpandClick = () => {
    setExpanded(!expanded);
  };

  return (
    <Box color="text.secondary" marginBottom={2}>
      <CollapseButton
        expanded={expanded}
        onClick={handleExpandClick}
        variant="mainOptions"
      >
        {t('options')}
      </CollapseButton>
      <Collapse in={expanded} timeout="auto" unmountOnExit>
        <Grid container spacing={2} mb={1} justifyContent="space-between">
          <Grid item xs={12} sm={6} md={3}>
            <IsPublicFilter
              value={filterParams.get('isPublic') ?? ''}
              onChange={(value) => setFilter('isPublic', value)}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={5} lg={4}>
            <RatingOrderByInput
              value={filterParams.get('orderBy') ?? ''}
              onChange={(value) => setFilter('orderBy', value)}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <MarkAllRatingsMenu onChange={onAllRatingsChange} />
          </Grid>
        </Grid>
      </Collapse>
    </Box>
  );
}

export default RatingsFilter;
