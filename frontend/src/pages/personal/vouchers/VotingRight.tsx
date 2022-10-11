import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Stack,
  Tooltip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
} from '@mui/material';
import InfoIcon from '@mui/icons-material/Info';
import TaskAltIcon from '@mui/icons-material/TaskAlt';
import RadioButtonUncheckedIcon from '@mui/icons-material/RadioButtonUnchecked';
import { useTranslation, Trans } from 'react-i18next';

import { AccountsService, UserProfile } from 'src/services/openapi';
import { usePersonalVouchers } from './context';

const Thumb = ({
  up,
  upDescription,
  downDescription,
}: {
  up: boolean | undefined;
  upDescription: string;
  downDescription: string;
}) => {
  if (up === undefined) return null;

  return (
    <Tooltip title={up ? upDescription : downDescription}>
      <IconButton>
        {up ? (
          <TaskAltIcon color="success" />
        ) : (
          <RadioButtonUncheckedIcon color="disabled" />
        )}
      </IconButton>
    </Tooltip>
  );
};

const DescriptionDialog = ({
  open,
  onClose,
}: {
  open: boolean;
  onClose: () => void;
}) => {
  const { t } = useTranslation();
  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>{t('personalVouchers.votingRight.title')}</DialogTitle>
      <DialogContent>
        <DialogContentText>
          <Trans t={t} i18nKey="personalVouchers.votingRight.description" />
        </DialogContentText>
      </DialogContent>
    </Dialog>
  );
};

const VotingRight = () => {
  const { t } = useTranslation();
  const [userProfile, setUserProfile] = React.useState<
    UserProfile | undefined
  >();
  const { receivedVouchers } = usePersonalVouchers();

  React.useEffect(() => {
    const loadUserProfile = async () => {
      const userProfile = await AccountsService.accountsProfileRetrieve();
      setUserProfile(userProfile);
    };
    loadUserProfile();
  }, []);

  const displayedValue = React.useMemo(() => {
    if (userProfile === undefined) return undefined;
    const { voting_right: votingRight } = userProfile;

    if (votingRight === undefined) return undefined;

    if (votingRight === null)
      return t('personalVouchers.votingRight.nullValue');

    if (votingRight < 0.2) return t('personalVouchers.votingRight.low');
    else if (votingRight < 0.8) return t('personalVouchers.votingRight.medium');
    else return t('personalVouchers.votingRight.high');
  }, [userProfile, t]);

  const [descriptionDialogOpen, setDescriptionDialogOpen] =
    React.useState(false);

  const handleDescriptionInfoClick = React.useCallback(() => {
    setDescriptionDialogOpen(true);
  }, []);

  const handleDescriptionDialogClose = React.useCallback(() => {
    setDescriptionDialogOpen(false);
  }, []);

  return (
    <Card sx={{ width: '100%' }}>
      <CardContent sx={{ height: '100%' }}>
        <Stack gap={1} sx={{ height: '100%' }}>
          <Stack direction="row" alignItems="center">
            <Typography color="text.secondary">
              {t('personalVouchers.votingRight.title')}
            </Typography>
            <IconButton onClick={handleDescriptionInfoClick}>
              <InfoIcon fontSize="small" />
            </IconButton>
            <DescriptionDialog
              open={descriptionDialogOpen}
              onClose={handleDescriptionDialogClose}
            />
          </Stack>
          <Box sx={{ display: 'flex', alignItems: 'center', height: '100%' }}>
            <Stack direction="row" alignItems="center" sx={{ width: '100%' }}>
              <Typography
                variant="h1"
                sx={{
                  flexGrow: 1,
                  textTransform: 'uppercase',
                }}
              >
                {displayedValue}
              </Typography>
              <Stack>
                <Thumb
                  up={userProfile?.is_trusted}
                  upDescription={t('personalVouchers.votingRight.isTrusted')}
                  downDescription={t(
                    'personalVouchers.votingRight.isNotTrusted'
                  )}
                />
                <Thumb
                  up={
                    receivedVouchers !== undefined
                      ? receivedVouchers.length > 0
                      : undefined
                  }
                  upDescription={t(
                    'personalVouchers.votingRight.hasReceivedVouchers'
                  )}
                  downDescription={t(
                    'personalVouchers.votingRight.hasNotReceivedVouchers'
                  )}
                />
              </Stack>
            </Stack>
          </Box>
        </Stack>
      </CardContent>
    </Card>
  );
};

export default VotingRight;
