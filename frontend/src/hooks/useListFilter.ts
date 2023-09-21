import { useLocation, useHistory } from 'react-router';

export const useListFilter = ({
  defaults = [],
  setEmptyValues = false,
}: {
  defaults?: Array<{ name: string; value: string }>;
  setEmptyValues?: boolean;
} = {}): [URLSearchParams, (key: string, value: string | null) => void] => {
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
    const oldValue = searchParams.get(key);
    let modified = false;
    if (value || (setEmptyValues && value === '')) {
      if (value !== oldValue) {
        searchParams.set(key, value);
        modified = true;
      }
    } else if (oldValue !== null) {
      searchParams.delete(key);
      modified = true;
    }
    if (modified) {
      // Reset pagination if any filter has changed
      if (key !== 'offset') {
        searchParams.delete('offset');
      }
      history.push({ search: searchParams.toString() });
    }
  };

  return [searchParams, setFilter];
};
