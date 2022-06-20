import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Box, Collapse, Grid } from '@mui/material';

import { CollapseButton } from 'src/components';
import { useListFilter } from 'src/hooks';
import IsPublicFilter from './IsPublicFilter';
import MarkAllRatingsMenu from './MarkAllRatings';

function RatingsFilter() {
  const { t } = useTranslation();
  const [expanded, setExpanded] = useState(false);
  const [filterParams, setFilter] = useListFilter();

  const handleExpandClick = () => {
    setExpanded(!expanded);
  };

  return (
    <Box color="text.secondary">
      <CollapseButton expanded={expanded} onClick={handleExpandClick}>
        {t('options')}
      </CollapseButton>
      <Collapse in={expanded} timeout="auto" unmountOnExit>
        <Grid container spacing={4} sx={{ marginBottom: '8px' }}>
          <Grid item xs={12} sm={6} md={5}>
            <IsPublicFilter
              value={filterParams.get('isPublic') ?? ''}
              onChange={(value) => setFilter('isPublic', value)}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={5}>
            <MarkAllRatingsMenu />
          </Grid>
        </Grid>
      </Collapse>
    </Box>
  );
}

export default RatingsFilter;
