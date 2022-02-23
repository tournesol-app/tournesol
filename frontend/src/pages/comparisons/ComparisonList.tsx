import React, { useState, useEffect } from 'react';
import { useLocation, useHistory } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import { ContentHeader, Pagination } from 'src/components';
import ComparisonList from 'src/features/comparisons/ComparisonList';
import type { Comparison } from 'src/services/openapi';
import { UsersService } from 'src/services/openapi';
import { UID_YT_NAMESPACE, YOUTUBE_POLL_NAME } from 'src/utils/constants';

function ComparisonsPage() {
  const { t } = useTranslation();
  const [comparisons, setComparisons]: [
    Comparison[] | undefined,
    (l: Comparison[] | undefined) => void
  ] = useState();
  const [count, setCount] = useState(0);
  const history = useHistory();
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const offset = Number(searchParams.get('offset') || 0);
  const filteredVideo = String(searchParams.get('video') || '');
  const limit = 20;

  function handleOffsetChange(newOffset: number) {
    searchParams.set('offset', newOffset.toString());
    history.push({ search: searchParams.toString() });
  }

  useEffect(() => {
    const process = async () => {
      const comparisonsRequest = await (filteredVideo
        ? UsersService.usersMeComparisonsListFiltered({
            pollName: YOUTUBE_POLL_NAME,
            uid: UID_YT_NAMESPACE + filteredVideo,
            limit,
            offset,
          })
        : UsersService.usersMeComparisonsList({
            pollName: YOUTUBE_POLL_NAME,
            limit,
            offset,
          }));
      setComparisons(comparisonsRequest.results);
      setCount(comparisonsRequest.count || 0);
    };
    process();

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.search]);

  return (
    <>
      <ContentHeader title={t('myComparisonsPage.title')} />
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          flexDirection: 'column',
          paddingBottom: 16,
          paddingTop: 16,
          gap: 16,
        }}
      >
        <Pagination
          offset={offset}
          count={count}
          onOffsetChange={handleOffsetChange}
          limit={limit}
          itemType={t('pagination.comparisons')}
        />
        <ComparisonList comparisons={comparisons} />
      </div>
    </>
  );
}

export default ComparisonsPage;
