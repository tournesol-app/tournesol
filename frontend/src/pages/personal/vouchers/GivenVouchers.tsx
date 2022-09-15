import React from 'react';
import { Box, Chip, Stack, Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';

import { useNotifications } from 'src/hooks';

import { usePersonalVouchers } from './context';

const GivenVoucherChip = ({ username }: { username: string }) => {
  const { t } = useTranslation();
  const { deleteGivenVoucher } = usePersonalVouchers();
  const { displayErrorsFrom, showSuccessAlert } = useNotifications();

  const handleDelete = React.useCallback(async () => {
    try {
      await deleteGivenVoucher({ username });
      showSuccessAlert(t('personalVouchers.givenVoucherDeleted', { username }));
    } catch (error) {
      displayErrorsFrom(error);
    }
  }, [deleteGivenVoucher, username, showSuccessAlert, displayErrorsFrom, t]);

  return (
    <Chip
      label={username}
      role="listitem"
      aria-label={username}
      onDelete={handleDelete}
    />
  );
};

const GivenVoucherList = () => {
  const { t } = useTranslation();
  const { givenVouchers } = usePersonalVouchers();

  if (givenVouchers === undefined) return null;

  if (givenVouchers.length === 0)
    return (
      <Typography paragraph>{t('personalVouchers.noVoucherGiven')}</Typography>
    );

  return (
    <Stack
      direction="row"
      flexWrap="wrap"
      gap={1}
      sx={{ py: 2 }}
      role="list"
      data-testid="given-vouchers-list"
    >
      {givenVouchers.map(({ to }) => (
        <GivenVoucherChip key={to} username={to} />
      ))}
    </Stack>
  );
};

const GivenVouchers = () => {
  const { t } = useTranslation();

  return (
    <Box py={2}>
      <Typography variant="h6">
        {t('personalVouchers.givenVouchersTitle')}
      </Typography>
      <GivenVoucherList />
    </Box>
  );
};

export default GivenVouchers;
