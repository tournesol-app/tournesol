import React from 'react';
import { useTranslation } from 'react-i18next';

import { IconButton } from '@mui/material';
import { Search } from '@mui/icons-material';

import { InternalLink } from 'src/components';

const SearchIconButtonLink = ({ params = '' }: { params?: string }) => {
  const { t } = useTranslation();
  const searchParams = params ? '?' + params : '';

  return (
    <InternalLink
      to={`/search${searchParams}`}
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
