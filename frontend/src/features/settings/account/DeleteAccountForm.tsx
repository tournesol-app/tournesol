import React, { useState } from 'react';
import { useTranslation, Trans } from 'react-i18next';
import { useHistory } from 'react-router-dom';

import { TextField, Typography, Button, useTheme } from '@mui/material';

import { useLoginState } from 'src/hooks';
import { UsersService } from 'src/services/openapi';
import { TRACKED_EVENTS, trackEvent } from 'src/utils/analytics';

const DELETE_ACCOUNT_KEYWORD = 'delete account';

const DeleteAccountForm = () => {
  const { t } = useTranslation();
  const theme = useTheme();
  const [keyword, setKeyword] = useState('');
  const { logout } = useLoginState();

  const history = useHistory();

  const deleteAccount = async () => {
    // TODO: track the event only when the deletion is successful
    await UsersService.usersMeDestroy();
    trackEvent(TRACKED_EVENTS.accountDeleted);
    logout();
    history.push('/');
  };

  return (
    <>
      <Typography>
        <Trans t={t} i18nKey="settings.typeKeywordDeleteAccount">
          Please type the words <b>{{ DELETE_ACCOUNT_KEYWORD }}</b> in the text
          box below to enable deleting your account.
        </Trans>
      </Typography>
      <TextField
        size="small"
        variant="outlined"
        color="secondary"
        value={keyword}
        onChange={(e) => setKeyword(e.target.value)}
        sx={{ width: '100%', margin: '8px 0px 8px 0px' }}
      />
      <Button
        disabled={keyword !== DELETE_ACCOUNT_KEYWORD}
        sx={{
          backgroundColor: theme.palette.error.main,
          color: theme.palette.error.contrastText,
          '&:hover': {
            backgroundColor: theme.palette.error.dark,
          },
        }}
        onClick={deleteAccount}
        fullWidth
        variant="contained"
      >
        {t('settings.deleteYourAccount')}
      </Button>
    </>
  );
};

export default DeleteAccountForm;
