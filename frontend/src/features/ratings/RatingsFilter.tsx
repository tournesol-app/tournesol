import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Box, Collapse, Grid } from '@mui/material';

import { CollapseButton } from 'src/components';
import { useListFilter } from 'src/hooks';

import IsPublicFilter from './IsPublicFilter';
import MarkAllRatingsMenu from './MarkAllRatings';
import RatingOrderByInput from './RatingOrderByInput';

const DEFAULT_FILTER_ORDER_BY = '-last_compared_at';

function RatingsFilter() {
  const { t } = useTranslation();
  const [expanded, setExpanded] = useState(false);
  const [filterParams, setFilter] = useListFilter();

  const handleExpandClick = () => {
    setExpanded(!expanded);
  };

  // Append default URL parameters if needed.
  useEffect(() => {
    const defaults = [{ key: 'orderBy', value: DEFAULT_FILTER_ORDER_BY }];

    defaults.map((param) => {
      if (!filterParams.get(param.key)) {
        setFilter(param.key, param.value);
      }
    });
  }, [filterParams, setFilter]);

  return (
    <Box color="text.secondary">
      <CollapseButton expanded={expanded} onClick={handleExpandClick}>
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
              value={filterParams.get('orderBy') ?? DEFAULT_FILTER_ORDER_BY}
              onChange={(value) => setFilter('orderBy', value)}
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
