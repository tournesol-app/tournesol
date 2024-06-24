import React from 'react';
import { useTranslation } from 'react-i18next';

import { IconButton } from '@mui/material';
import { Undo } from '@mui/icons-material';

import { InternalLink } from 'src/components';

const BackIconButton = ({ path = '' }: { path: string }) => {
  const { t } = useTranslation();
  return (
    <InternalLink
      to={path}
      ariaLabel={t('backIconButton.backToThePreviousPage')}
    >
      <IconButton color="secondary">
        <Undo />
      </IconButton>
    </InternalLink>
  );
};

export default BackIconButton;
