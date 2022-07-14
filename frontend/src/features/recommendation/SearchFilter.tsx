import React, { useState, useCallback } from 'react';
import { Collapse, Grid, Box } from '@mui/material';

import { CollapseButton } from 'src/components';
import { useCurrentPoll, useListFilter } from 'src/hooks';
import DurationFilter from 'src/features/recommendation/DurationFilter';
import LanguageFilter from './LanguageFilter';
import DateFilter from './DateFilter';
import CriteriaFilter from './CriteriaFilter';
import UploaderFilter from './UploaderFilter';
import AdvancedFilter from './AdvancedFilter';
import ScoreModeFilter from './ScoreModeFilter';
import {
  recommendationFilters,
  defaultRecommendationFilters,
  YOUTUBE_POLL_NAME,
  PRESIDENTIELLE_2022_POLL_NAME,
} from 'src/utils/constants';
import { ScoreModeEnum } from 'src/utils/api/recommendations';
import { saveRecommendationsLanguages } from 'src/utils/recommendationsLanguages';

/**
 * Filter options for Videos recommendations
 *
 * The "filters" button has a badge when one of its filter is enabled with a non-default value.
 * When adding a new filter, it needs to be defined in constants 'recommendationFilters'
 * and 'defaultRecommendationsFilters'.
 */
function SearchFilter() {
  const [expanded, setExpanded] = useState(false);
  const [filterParams, setFilter] = useListFilter({ setEmptyValues: true });

  const { name: pollName } = useCurrentPoll();

  const handleExpandClick = () => {
    setExpanded(!expanded);
  };

  const isFilterActive = () =>
    Object.entries(defaultRecommendationFilters).some(
      ([key, defaultValue]) =>
        ![null, '', defaultValue].includes(filterParams.get(key))
    );

  const handleLanguageChange = useCallback(
    (value: string) => {
      saveRecommendationsLanguages(value);
      setFilter(recommendationFilters.language, value);
    },
    [setFilter]
  );

  const setFilterCallback = useCallback(
    (filter) => setFilter(filter.param, filter.value),
    [setFilter]
  );

  return (
    <Box color="text.secondary">
      <CollapseButton
        expanded={expanded}
        onClick={handleExpandClick}
        showBadge={isFilterActive()}
      />
      <Collapse in={expanded} timeout="auto" unmountOnExit>
        {filterParams.get(recommendationFilters.uploader) && (
          <Box marginBottom={1}>
            <UploaderFilter
              value={filterParams.get(recommendationFilters.uploader) ?? ''}
              onDelete={() => setFilter(recommendationFilters.uploader, '')}
            />
          </Box>
        )}
        <Grid container spacing={4} sx={{ marginBottom: '8px' }}>
          {pollName === YOUTUBE_POLL_NAME && (
            <>
              <Grid
                item
                xs={6}
                md={3}
                lg={3}
                data-testid="search-date-safe-filter"
              >
                <DateFilter
                  value={filterParams.get(recommendationFilters.date) ?? ''}
                  onChange={(value) =>
                    setFilter(recommendationFilters.date, value)
                  }
                />
                <Box mt={2}>
                  <AdvancedFilter
                    value={filterParams.get('unsafe') ?? ''}
                    onChange={(value) => setFilter('unsafe', value)}
                  />
                </Box>
              </Grid>
              <Grid
                item
                xs={6}
                md={3}
                lg={3}
                data-testid="search-language-filter"
              >
                <LanguageFilter
                  value={filterParams.get(recommendationFilters.language) ?? ''}
                  onChange={handleLanguageChange}
                />
                <Box mt={2}>
                  <DurationFilter
                    valueMax={filterParams.get('duration_lte') ?? ''}
                    valueMin={filterParams.get('duration_gte') ?? ''}
                    onChangeCallback={setFilterCallback}
                  />
                </Box>
              </Grid>
            </>
          )}
          <Grid item xs={12} sm={12} md={6}>
            <CriteriaFilter setFilter={setFilter} />
          </Grid>
          {pollName == PRESIDENTIELLE_2022_POLL_NAME && (
            <Grid item xs={12} sm={4}>
              <ScoreModeFilter
                value={filterParams.get('score_mode') ?? ScoreModeEnum.DEFAULT}
                onChange={(value) => setFilter('score_mode', value)}
              />
            </Grid>
          )}
        </Grid>
      </Collapse>
    </Box>
  );
}

export default SearchFilter;
