import { useCallback } from 'react';
import { useLocation, useHistory } from 'react-router';

export const useListFilter = ({
  setEmptyValues = false,
}: { setEmptyValues?: boolean } = {}): [
  URLSearchParams,
  (key: string, value: string) => void
] => {
  const location = useLocation();
  const history = useHistory();
  const searchParams = new URLSearchParams(location.search);

  const setFilter = useCallback(
    (key: string, value: string) => {
      if (value || setEmptyValues) {
        searchParams.set(key, value);
      } else {
        searchParams.delete(key);
      }
      // Reset pagination if filters change
      if (key !== 'offset') {
        searchParams.delete('offset');
      }
      history.push({ search: searchParams.toString() });
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [setEmptyValues]
  );

  return [searchParams, setFilter];
};
