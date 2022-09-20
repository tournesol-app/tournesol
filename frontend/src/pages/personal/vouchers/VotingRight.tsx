import React from 'react';
import { Box, Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';

import { AccountsService } from 'src/services/openapi';

const VotingRight = () => {
  const { t } = useTranslation();
  const [votingRight, setVotingRight] = React.useState<
    number | null | undefined
  >();

  React.useEffect(() => {
    const loadVotingRight = async () => {
      const userProfile = await AccountsService.accountsProfileRetrieve();
      setVotingRight(userProfile['voting_right']);
    };
    loadVotingRight();
  }, []);

  const displayedValue = React.useMemo(() => {
    if (votingRight === undefined) return undefined;

    if (votingRight === null)
      return t('personalVouchers.votingRight.nullValue');

    const percentage = Math.round(votingRight * 100).toString();
    return t('personalVouchers.votingRight.percentage', {
      value: percentage,
    });
  }, [votingRight, t]);

  return (
    <Box py={2}>
      <Typography variant="h6">
        {t('personalVouchers.votingRight.title')}
      </Typography>
      <Typography paragraph>
        {t('personalVouchers.votingRight.description')}
      </Typography>
      {displayedValue !== undefined && (
        <Typography paragraph>
          {t('personalVouchers.votingRight.value', {
            value: displayedValue,
          })}
        </Typography>
      )}
    </Box>
  );
};

export default VotingRight;
