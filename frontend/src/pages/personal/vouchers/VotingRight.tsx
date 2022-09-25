import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Stack,
  Tooltip,
  IconButton,
} from '@mui/material';
import InfoIcon from '@mui/icons-material/Info';
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

    if (votingRight < 0.2) return t('personalVouchers.votingRight.low');
    else if (votingRight < 0.8) return t('personalVouchers.votingRight.medium');
    else return t('personalVouchers.votingRight.high');
  }, [votingRight, t]);

  return (
    <Card sx={{ width: '100%' }}>
      <CardContent sx={{ height: '100%' }}>
        <Stack gap={1} sx={{ height: '100%' }}>
          <Stack direction="row" alignItems="center">
            <Typography color="text.secondary">
              {t('personalVouchers.votingRight.title')}
            </Typography>
            <Tooltip title={t('personalVouchers.votingRight.description')}>
              <IconButton>
                <InfoIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Stack>
          <Box sx={{ display: 'flex', alignItems: 'center', height: '100%' }}>
            <Typography variant="h1">{displayedValue}</Typography>
          </Box>
        </Stack>
      </CardContent>
    </Card>
  );
};

export default VotingRight;
