import React from 'react';
import { useTranslation } from 'react-i18next';
import { Box, Chip, Typography } from '@mui/material';
import zxcvbn from 'zxcvbn-ts';

const PasswordStrengthIndicator = ({ passwd }: { passwd: string }) => {
  const { t } = useTranslation();

  const result = zxcvbn(passwd);

  const passwordStrengths = [
    {
      score: 0,
      label: t('passwordStrengthIndicator.strength.veryWeak'),
      color: 'error',
      testId: 'passwd_str_veryweak',
    },
    {
      score: 1,
      label: t('passwordStrengthIndicator.strength.weak'),
      color: 'warning',
      testId: 'passwd_str_weak',
    },
    {
      score: 2,
      label: t('passwordStrengthIndicator.strength.medium'),
      color: 'info',
      testId: 'passwd_str_medium',
    },
    {
      score: 3,
      label: t('passwordStrengthIndicator.strength.strong'),
      color: 'success',
      testId: 'passwd_str_strong',
    },
    {
      score: 4,
      label: t('passwordStrengthIndicator.strength.veryStrong'),
      color: 'success',
      testId: 'passwd_str_verystrong',
    },
  ] as const;

  return (
    <>
      <Typography gutterBottom>
        {t('passwordStrengthIndicator.passwordStrength')}
      </Typography>
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
        {passwordStrengths.map((strength) => {
          const disabled = passwd === '' || strength.score != result.score;
          return (
            <Chip
              key={strength.score}
              size="small"
              label={strength.label}
              color={strength.color}
              disabled={disabled}
              data-disabled={disabled}
              data-testid={strength.testId}
              sx={(t) => ({ [t.breakpoints.down('sm')]: { fontSize: '11px' } })}
            />
          );
        })}
      </Box>
    </>
  );
};

export default PasswordStrengthIndicator;
