import { useLocation, useHistory } from 'react-router';

export const useListFilter = (): [
  URLSearchParams,
  (key: string, value: string) => void
] => {
  const location = useLocation();
  const history = useHistory();
  const searchParams = new URLSearchParams(location.search);

  const setFilter = (key: string, value: string) => {
    if (value) {
      searchParams.set(key, value);
    } else {
      searchParams.delete(key);
    }
    // Reset pagination if filters change
    if (key !== 'offset') {
      searchParams.delete('offset');
    }
    history.push({ search: searchParams.toString() });
  };

  return [searchParams, setFilter];
};
