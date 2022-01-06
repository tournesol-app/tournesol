import React, { useState, useEffect } from 'react';
import { useLocation, useHistory } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import type { Comparison } from 'src/services/openapi';
import { UsersService } from 'src/services/openapi';
import ComparisonList from 'src/features/comparisons/ComparisonList';
import Pagination from 'src/components/Pagination';

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
  const limit = 20;

  function handleOffsetChange(newOffset: number) {
    history.push(`/comparisons/?offset=${newOffset}`);
  }

  useEffect(() => {
    UsersService.usersMeComparisonsList({ limit, offset }).then((data) => {
      setComparisons(data.results);
      setCount(data.count || 0);
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [offset]);

  return (
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
  );
}

export default ComparisonsPage;
