import React from 'react';
import { useTranslation } from 'react-i18next';

import { IconButton } from '@mui/material';
import { Search } from '@mui/icons-material';

import { InternalLink } from 'src/components';

/**
 * Where the search page's back button should return to, carried as the
 * search link's location state and read there via `useLocation().state`.
 */
export interface BackNavigationState {
  backPath: string;
  backParams?: string;
}

const SearchIconButtonLink = ({
  params = '',
  backNavigation,
}: {
  params?: string;
  backNavigation?: BackNavigationState;
}) => {
  const { t } = useTranslation();
  const searchParams = params ? '?' + params : '';

  return (
    <InternalLink
      to={`/search${searchParams}`}
      state={backNavigation}
      ariaLabel={t('searchButtonLink.linkToTheSearchPage')}
      data-testid="icon-link-to-search-page"
    >
      <IconButton color="secondary">
        <Search />
      </IconButton>
    </InternalLink>
  );
};

export default SearchIconButtonLink;
