import React from 'react';
import { useTranslation } from 'react-i18next';
import { Box, Chip, Typography } from '@mui/material';
import zxcvbn from 'zxcvbn-ts';

const PasswordStrengthIndicator = ({ pwd }: { pwd: string }) => {
  const { t } = useTranslation();

  const result = zxcvbn(pwd);

  const passwordStrengths = [
    {
      score: 0,
      label: t('passwordStrengthIndicator.strength.veryWeak'),
      color: 'error',
    },
    {
      score: 1,
      label: t('passwordStrengthIndicator.strength.weak'),
      color: 'warning',
    },
    {
      score: 2,
      label: t('passwordStrengthIndicator.strength.medium'),
      color: 'info',
    },
    {
      score: 3,
      label: t('passwordStrengthIndicator.strength.strong'),
      color: 'success',
    },
    {
      score: 4,
      label: t('passwordStrengthIndicator.strength.veryStrong'),
      color: 'success',
    },
  ] as const;

  return (
    <>
      <Typography gutterBottom>
        {t('passwordStrengthIndicator.passwordStrength')}
      </Typography>
      <Box
        sx={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: 1 }}
      >
        {passwordStrengths.map((strength) => (
          <Chip
            key={strength.score}
            size="small"
            label={strength.label}
            color={strength.color}
            disabled={pwd === '' || strength.score != result.score}
          />
        ))}
      </Box>
    </>
  );
};

export default PasswordStrengthIndicator;
