import { useLocation } from 'react-router';

import { useUpdateSearchParams } from './useUpdateSearchParams';

export const useListFilter = ({
  defaults = [],
  setEmptyValues = false,
}: {
  defaults?: Array<{ name: string; value: string }>;
  setEmptyValues?: boolean;
} = {}): [URLSearchParams, (key: string, value: string | null) => void] => {
  const location = useLocation();
  const updateSearchParams = useUpdateSearchParams();
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

      updateSearchParams(searchParams.toString());
    }
  };

  return [searchParams, setFilter];
};
