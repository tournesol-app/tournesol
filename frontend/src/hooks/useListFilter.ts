import { useLocation, useHistory } from 'react-router';

export const useListFilter = ({
  defaults = [],
  setEmptyValues = false,
}: {
  defaults?: Array<{ name: string; value: string }>;
  setEmptyValues?: boolean;
} = {}): [URLSearchParams, (key: string, value: string) => void] => {
  const location = useLocation();
  const history = useHistory();
  const searchParams = new URLSearchParams(location.search);

  // Initialize the filters with the default values provided.
  defaults.map((param) => {
    if (!searchParams.get(param.name)) {
      searchParams.set(param.name, param.value);
    }
  });

  const setFilter = (key: string, value: string | null) => {
    if (value || (setEmptyValues && value === '')) {
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
