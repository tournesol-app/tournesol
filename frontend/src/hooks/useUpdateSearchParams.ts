import { useCallback } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

/**
 * Update the query string of the current page.
 *
 * This is the write counterpart to `useSearchParams`: it stays on the current
 * path and only changes the search parameters. Because the navigation doesn't
 * leave the page, the current `location.state` is carried forward. React
 * Router would otherwise reset it to `null`, dropping data that belongs to the
 * current visit (for instance the search page's back-button target, kept in
 * the location state while the user changes filters or turns pages).
 */
export const useUpdateSearchParams = () => {
  const navigate = useNavigate();
  const location = useLocation();

  return useCallback(
    (search: string, { replace = false }: { replace?: boolean } = {}) => {
      navigate({ search }, { replace, state: location.state });
    },
    [navigate, location.state]
  );
};
