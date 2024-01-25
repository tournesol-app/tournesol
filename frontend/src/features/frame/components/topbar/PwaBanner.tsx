import React, { useState } from 'react';
import { BeforeInstallPromptEvent } from '../../pwaPrompt';
import { Avatar, Button, Grid, Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';

const pwaBannerIgnoredKey = 'pwaBannerIgnoredAt';

const hasPwaBannerBeenIgnored = () => {
  try {
    const value = localStorage.getItem(pwaBannerIgnoredKey);
    return value != null;
  } catch {
    return true;
  }
};

interface Props {
  beforeInstallPromptEvent?: BeforeInstallPromptEvent;
}

const PwaBanner = ({ beforeInstallPromptEvent }: Props) => {
  const { t } = useTranslation();
  const [pwaBannerVisible, setPwaBannerVisible] = useState(
    () => !hasPwaBannerBeenIgnored()
  );

  if (!beforeInstallPromptEvent || !pwaBannerVisible) {
    return null;
  }

  return (
    <Grid
      container
      p={2}
      sx={(theme) => ({
        backgroundColor: theme.palette.neutral.light,
        color: theme.palette.text.primary,
      })}
      gap={2}
      alignItems="center"
    >
      <Typography fontWeight="bold" display="flex" gap={1}>
        <Avatar
          component="span"
          src="/icons/maskable-icon-512x512.png"
          sx={{ width: '48px', height: '48px' }}
        />
        {t('pwaBanner.message')}
      </Typography>
      <Grid item container justifyContent="right" columnGap={1}>
        <Button
          variant="text"
          color="inherit"
          onClick={() => {
            setPwaBannerVisible(false);
            localStorage.setItem(pwaBannerIgnoredKey, new Date().toISOString());
          }}
        >
          {t('pwaBanner.ignore')}
        </Button>
        <Button
          variant="contained"
          onClick={() => beforeInstallPromptEvent.prompt()}
        >
          {t('pwaBanner.install')}
        </Button>
      </Grid>
    </Grid>
  );
};

export default PwaBanner;
