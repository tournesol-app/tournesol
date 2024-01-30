import React from 'react';
import { Link } from 'react-router-dom';

import { IconButton } from '@mui/material';
import { Settings } from '@mui/icons-material';
import { useTranslation } from 'react-i18next';

const PreferencesIconButtonLink = ({ hash = '' }: { hash?: string }) => {
  const { t } = useTranslation();

  return (
    <Link
      aria-label={t('preferencesIconButtonLink.linkToThePreferencesPage')}
      to={`/settings/preferences${hash}`}
    >
      <IconButton color="secondary">
        <Settings />
      </IconButton>
    </Link>
  );
};

export default PreferencesIconButtonLink;
