import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Stack,
  IconButton,
} from '@mui/material';
import InfoIcon from '@mui/icons-material/Info';
import TaskAltIcon from '@mui/icons-material/TaskAlt';
import RadioButtonUncheckedIcon from '@mui/icons-material/RadioButtonUnchecked';
import { useTranslation } from 'react-i18next';

import { AccountsService, UserProfile } from 'src/services/openapi';
import DialogBox from 'src/components/DialogBox';

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
    <Stack direction="row" alignItems="center">
      <IconButton>
        {up ? (
          <TaskAltIcon color="success" />
        ) : (
          <RadioButtonUncheckedIcon color="disabled" />
        )}
      </IconButton>
      <Typography paragraph mb={0}>
        {up ? upDescription : downDescription}
      </Typography>
    </Stack>
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
  const dialog = React.useMemo(
    () => ({
      title: t('personalVouchers.trustScore.title'),
      messages: [
        t('personalVouchers.trustScore.description.explanation'),
        t('personalVouchers.trustScore.description.howToChangeIt'),
        t('personalVouchers.trustScore.description.includedInPublicDatabase'),
      ],
    }),
    [t]
  );
  return <DialogBox open={open} onClose={onClose} dialog={dialog} />;
};

const TrustScore = () => {
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
    const { trust_score: trustScore } = userProfile;

    if (trustScore === undefined) return undefined;

    if (trustScore === null) return t('personalVouchers.trustScore.nullValue');

    if (trustScore < 0.2) return t('personalVouchers.trustScore.low');
    else if (trustScore < 0.8) return t('personalVouchers.trustScore.medium');
    else return t('personalVouchers.trustScore.high');
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
              {t('personalVouchers.trustScore.title')}
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
            <Stack
              direction="column"
              alignItems="center"
              sx={{ width: '100%' }}
              spacing={2}
            >
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
                  upDescription={t('personalVouchers.trustScore.isTrusted')}
                  downDescription={t(
                    'personalVouchers.trustScore.isNotTrusted'
                  )}
                />
                <Thumb
                  up={
                    receivedVouchers !== undefined
                      ? receivedVouchers.length > 0
                      : undefined
                  }
                  upDescription={t(
                    'personalVouchers.trustScore.hasReceivedVouchers'
                  )}
                  downDescription={t(
                    'personalVouchers.trustScore.hasNotReceivedVouchers'
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

export default TrustScore;
