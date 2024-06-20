import React from 'react';
import { useTranslation } from 'react-i18next';

import { IconButton } from '@mui/material';
import { Search } from '@mui/icons-material';

import { InternalLink } from 'src/components';

const SearchIconButtonLink = () => {
  const { t } = useTranslation();

  return (
    <InternalLink
      to={`/search`}
      ariaLabel={t('searchButtonLink.linkToTheSearchPage')}
    >
      <IconButton color="secondary">
        <Search />
      </IconButton>
    </InternalLink>
  );
};

export default SearchIconButtonLink;
