import React from 'react';
import { Box, Chip, Stack, Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';

import { usePersonalVouchers } from './context';

const VoucherChip = ({ username }: { username: string }) => (
  <Chip label={username} role="listitem" aria-label={username} />
);

const ReceivedVoucherList = () => {
  const { t } = useTranslation();
  const { receivedVouchers } = usePersonalVouchers();

  if (receivedVouchers === undefined) return null;

  if (receivedVouchers.length === 0)
    return (
      <Typography
        sx={{
          marginBottom: '16px',
        }}
      >
        {t('personalVouchers.noVoucherReceived')}
      </Typography>
    );

  return (
    <Stack
      direction="row"
      role="list"
      data-testid="received-vouchers-list"
      sx={{
        flexWrap: 'wrap',
        gap: 1,
        py: 2,
      }}
    >
      {receivedVouchers.map(({ by }) => (
        <VoucherChip key={by} username={by} />
      ))}
    </Stack>
  );
};

const ReceivedVouchers = () => {
  const { t } = useTranslation();

  return (
    <Box
      sx={{
        py: 2,
      }}
    >
      <Typography variant="h6">
        {t('personalVouchers.receivedVouchersTitle')}
      </Typography>
      <ReceivedVoucherList />
    </Box>
  );
};

export default ReceivedVouchers;
