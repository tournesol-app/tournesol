import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';

import type { Comparison } from 'src/services/openapi';
import { selectLogin } from 'src/features/login/loginSlice';
import { fetchComparisons } from 'src/features/comparisons/comparisonsAPI';
import ComparisonList from 'src/features/comparisons/ComparisonList';

import { useAppSelector } from '../../app/hooks';

function ComparisonsPage() {
  const token = useAppSelector(selectLogin);
  const [comparisons, setComparisons]: [
    Comparison[] | undefined,
    (l: Comparison[] | undefined) => void
  ] = useState();
  const [count, setCount] = useState(0);
  const paramsString = useLocation().search;
  const searchParams = new URLSearchParams(paramsString);
  const page = Number(searchParams.get('page') || 1);
  const [limit, offset] = [30, 30 * (page - 1)];

  useEffect(() => {
    fetchComparisons(token?.access_token ?? '', limit, offset).then((data) => {
      setComparisons(data.results);
      setCount(data.count || 0);
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page]);

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        flexDirection: 'column',
        paddingBottom: 32,
      }}
    >
      <span style={{ marginTop: 32 }}>
        {offset + 1} to {Math.min(count, offset + limit)} of {count}
      </span>
      {offset + limit < count && <Link to={`?page=${page + 1}`}>next</Link>}
      <ComparisonList comparisons={comparisons} />
    </div>
  );
}

export default ComparisonsPage;
