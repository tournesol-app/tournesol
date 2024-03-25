import React, { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useHistory, Link } from 'react-router-dom';

import { Box, Button, Divider } from '@mui/material';

import type { PaginatedContributorRatingList } from 'src/services/openapi';
import Pagination from 'src/components/Pagination';
import { UsersService } from 'src/services/openapi';
import { ContentBox, ContentHeader, LoaderWrapper } from 'src/components';
import RatingsFilter from 'src/features/ratings/RatingsFilter';
import { scrollToTop } from 'src/utils/ui';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import EntityList from 'src/features/entities/EntityList';

const DEFAULT_FILTER_ORDER_BY = '-last_compared_at';

const NoRatingMessage = ({ hasFilter }: { hasFilter: boolean }) => {
  const { t } = useTranslation();
  return (
    <>
      <Divider />
      {hasFilter ? (
        <Box my={2}>{t('ratings.noVideoCorrespondsToFilter')}</Box>
      ) : (
        <>
          <Box my={2}>
            {t('ratings.noVideoComparedYet')}
            {' 🥺'}
          </Box>
          <Button
            component={Link}
            to="/comparison"
            variant="contained"
            color="primary"
          >
            {t('ratings.compareVideosButton')}
          </Button>
        </>
      )}
    </>
  );
};

const VideoRatingsPage = () => {
  const { name: pollName, options } = useCurrentPoll();
  const [ratings, setRatings] = useState<PaginatedContributorRatingList>({});
  const [isLoading, setIsLoading] = useState(true);
  const location = useLocation();
  const history = useHistory();
  const { t } = useTranslation();
  const searchParams = new URLSearchParams(location.search);
  const limit = 20;
  const offset = Number(searchParams.get('offset') || 0);
  const videoCount = ratings.count || 0;
  const hasFilter = searchParams.get('isPublic') != null;

  const handleOffsetChange = (newOffset: number) => {
    searchParams.set('offset', newOffset.toString());
    history.push({ search: searchParams.toString() });
    scrollToTop();
  };

  const loadData = useCallback(async () => {
    setIsLoading(true);
    const urlParams = new URLSearchParams(location.search);
    const isPublicParam = urlParams.get('isPublic');
    const orderByParam = urlParams.get('orderBy') || DEFAULT_FILTER_ORDER_BY;

    const isPublic = isPublicParam ? isPublicParam === 'true' : undefined;
    const orderBy = orderByParam ?? undefined;

    const response = await UsersService.usersMeContributorRatingsList({
      pollName,
      limit,
      offset,
      isPublic,
      orderBy,
    });

    setRatings(response);
    setIsLoading(false);
  }, [offset, location.search, pollName]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const onAllRatingsChange = () => {
    if (hasFilter) {
      // A filter had been selected. Let's reset the filter to reload the list.
      searchParams.delete('isPublic');
      history.push({ search: searchParams.toString() });
    } else {
      // No filter is selected. Let's simply refresh the list.
      loadData();
    }
  };

  return (
    <>
      <ContentHeader title={t('myRatedVideosPage.title')} />
      <ContentBox noMinPaddingX maxWidth="lg">
        {options?.comparisonsCanBePublic === true && (
          <Box px={{ xs: 2, sm: 0 }}>
            <RatingsFilter
              defaultFilters={[
                { name: 'orderBy', value: DEFAULT_FILTER_ORDER_BY },
              ]}
              onAllRatingsChange={onAllRatingsChange}
            />
          </Box>
        )}
        <LoaderWrapper isLoading={isLoading}>
          <EntityList
            entities={ratings.results}
            emptyMessage={<NoRatingMessage hasFilter={hasFilter} />}
            cardProps={{ showRatingControl: true }}
            displayContextAlert={true}
          />
        </LoaderWrapper>
        {!isLoading && videoCount > 0 && videoCount > limit && (
          <Pagination
            offset={offset}
            count={videoCount}
            onOffsetChange={handleOffsetChange}
            limit={limit}
          />
        )}
      </ContentBox>
    </>
  );
};

export default VideoRatingsPage;
