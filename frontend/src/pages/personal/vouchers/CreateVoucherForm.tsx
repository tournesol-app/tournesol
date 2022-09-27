import React, { useState, useCallback } from 'react';
import { useTranslation } from 'react-i18next';

import { TextField, Button, Typography, Grid } from '@mui/material';
import { HowToReg } from '@mui/icons-material';

import { useNotifications } from 'src/hooks';
import { usePersonalVouchers } from './context';

const inputProps = {
  // If not set some browsers may auto fill the input with a saved username
  // because the input label in English is "Username".
  autoComplete: 'new-password',
};

const CreateVoucherForm = () => {
  const { t } = useTranslation();
  const [username, setUsername] = useState<string>('');
  const { displayErrorsFrom, showSuccessAlert } = useNotifications();
  const { createVoucher } = usePersonalVouchers();

  const handleUsernameChange = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      setUsername(event.target.value);
    },
    []
  );

  const handleSubmit = useCallback(
    async (event: React.FormEvent<HTMLFormElement>) => {
      event.preventDefault();
      try {
        await createVoucher({ username });
        showSuccessAlert(t('personalVouchers.voucherCreated', { username }));
        setUsername('');
      } catch (error) {
        displayErrorsFrom(error);
      }
    },
    [username, createVoucher, t, showSuccessAlert, displayErrorsFrom]
  );

  return (
    <form onSubmit={handleSubmit}>
      <Typography paragraph>{t('personalVouchers.introduction')}</Typography>
      <Grid container gap={2} justifyContent="flex-start">
        <TextField
          label={t('personalVouchers.usernameLabel')}
          value={username}
          onChange={handleUsernameChange}
          inputProps={inputProps}
          size="small"
          variant="outlined"
          required
        />
        <Button
          type="submit"
          variant="contained"
          endIcon={<HowToReg />}
          disableElevation
        >
          {t('personalVouchers.submitButton')}
        </Button>
      </Grid>
    </form>
  );
};

export default CreateVoucherForm;
