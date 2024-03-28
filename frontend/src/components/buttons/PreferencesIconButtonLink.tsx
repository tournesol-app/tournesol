import React from 'react';
import { useTranslation } from 'react-i18next';

import { IconButton } from '@mui/material';
import { Settings } from '@mui/icons-material';

import { InternalLink } from 'src/components';

const PreferencesIconButtonLink = ({ hash = '' }: { hash?: string }) => {
  const { t } = useTranslation();

  return (
    <InternalLink
      to={`/settings/preferences${hash}`}
      ariaLabel={t('preferencesIconButtonLink.linkToThePreferencesPage')}
    >
      <IconButton color="secondary">
        <Settings />
      </IconButton>
    </InternalLink>
  );
};

export default PreferencesIconButtonLink;
