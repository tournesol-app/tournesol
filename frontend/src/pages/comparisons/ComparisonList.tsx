import React, { useState, useEffect } from 'react';
import { useLocation, useHistory, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import { Box, Button, Typography } from '@mui/material';
import { ContentHeader, LoaderWrapper, Pagination } from 'src/components';
import ComparisonList from 'src/features/comparisons/ComparisonList';
import type { Comparison } from 'src/services/openapi';
import { UsersService } from 'src/services/openapi';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';

function ComparisonsPage() {
  const { t } = useTranslation();
  const { name: pollName, baseUrl } = useCurrentPoll();
  const [comparisons, setComparisons]: [
    Comparison[] | undefined,
    (l: Comparison[] | undefined) => void
  ] = useState();
  const [comparisonCount, setCount] = useState(0);
  const history = useHistory();
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const offset = Number(searchParams.get('offset') || 0);
  const filteredUid = String(searchParams.get('uid') || '');
  const limit = 20;

  function handleOffsetChange(newOffset: number) {
    searchParams.set('offset', newOffset.toString());
    history.push({ search: searchParams.toString() });
  }

  useEffect(() => {
    const process = async () => {
      const comparisonsRequest = await (filteredUid
        ? UsersService.usersMeComparisonsListFiltered({
          pollName,
          uid: filteredUid,
          limit,
          offset,
        })
        : UsersService.usersMeComparisonsList({
          pollName,
          limit,
          offset,
        }));
      setComparisons(comparisonsRequest.results);
      setCount(comparisonsRequest.count || 0);
    };
    process();

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.search]);

  const noComparisonMessage = (
    <>
      <Typography variant="h5" paragraph>
        {t('myComparisonsPage.noComparisonYet')}
      </Typography>
      <Box display="flex" justifyContent="center">
        <Button
          component={Link}
          to={`${baseUrl}/comparison?series=true`}
          variant="contained"
          color="primary"
        >
          {t('menu.compare')}
        </Button>
      </Box>
    </>
  );

  return (
    <>
      <ContentHeader title={t('myComparisonsPage.title')} />
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          flexDirection: 'column',
          py: 2,
          gap: 2,
        }}
      >
        <LoaderWrapper isLoading={comparisons == undefined}>
          {comparisonCount === 0 ? (
            noComparisonMessage
          ) : (
            <>
              <ComparisonList comparisons={comparisons} />
              <Pagination
                offset={offset}
                count={comparisonCount}
                onOffsetChange={handleOffsetChange}
                limit={limit}
                itemType={t('pagination.comparisons')}
              />
            </>
          )}
        </LoaderWrapper>
      </Box>
    </>
  );
}

export default ComparisonsPage;
