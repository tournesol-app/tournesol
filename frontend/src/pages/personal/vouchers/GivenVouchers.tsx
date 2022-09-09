import React from 'react';
import { Box, Chip, Stack, Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';

import { usePersonalVouchers } from './context';

const GivenVoucherChip = ({ username }: { username: string }) => (
  <Chip label={username} role="listitem" aria-label={username} />
);

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
      spacing={1}
      direction="row"
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
