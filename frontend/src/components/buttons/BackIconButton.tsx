import React, { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useDispatch } from 'react-redux';

import { IconButton } from '@mui/material';
import { Undo } from '@mui/icons-material';

import { InternalLink } from 'src/components';
import { clearBackNavigation } from 'src/features/login/loginSlice';

const BackIconButton = ({ path = '' }: { path: string }) => {
  const { t } = useTranslation();
  const dispatch = useDispatch();

  useEffect(() => {
    return () => {
      dispatch(clearBackNavigation());
    };
  }, [dispatch]);

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
