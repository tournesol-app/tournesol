import React from 'react';
import { Link } from 'react-router-dom';

import { IconButton } from '@mui/material';
import { Settings } from '@mui/icons-material';

const PreferencesIconButtonLink = ({ hash = '' }: { hash?: string }) => {
  return (
    <Link
      aria-label="Link to the preferences page"
      to={`settings/preferences${hash}`}
    >
      <IconButton>
        <Settings />
      </IconButton>
    </Link>
  );
};

export default PreferencesIconButtonLink;
