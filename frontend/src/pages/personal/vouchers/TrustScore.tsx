import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';

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

import DialogBox from 'src/components/DialogBox';
import { AccountsService, UserProfile } from 'src/services/openapi';
import { usePersonalVouchers } from './context';

const TRUST_SCORE_LOW = 0.1;
const TRUST_SCORE_MEDIUM = 0.5;
const TRUST_SCORE_LOW_COLOR = 'text.secondary';
const TRUST_SCORE_MEDIUM_COLOR = '#506AD4';
const TRUST_SCORE_HIGH_COLOR = '#2e7d32';

const getTrustScoreColor = (trustScore: number | null | undefined) => {
  if (!trustScore || trustScore < TRUST_SCORE_LOW) {
    return TRUST_SCORE_LOW_COLOR;
  }

  if (trustScore < TRUST_SCORE_MEDIUM) {
    return TRUST_SCORE_MEDIUM_COLOR;
  }

  return TRUST_SCORE_HIGH_COLOR;
};

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
    <Stack direction="row" gap={1} alignItems="center">
      {up ? (
        <TaskAltIcon color="success" />
      ) : (
        <RadioButtonUncheckedIcon color="disabled" />
      )}
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
  const dialog = useMemo(
    () => ({
      title: t('personalVouchers.trustScore.title'),
      content: [
        t('personalVouchers.trustScore.description.explanation'),
        t('personalVouchers.trustScore.description.howToChangeIt'),
        t('personalVouchers.trustScore.description.includedInPublicDatabase'),
      ].map((message, index) => {
        return (
          <Typography key={index} paragraph>
            {message}
          </Typography>
        );
      }),
    }),
    [t]
  );
  return (
    <DialogBox
      open={open}
      onClose={onClose}
      title={dialog.title}
      content={dialog.content}
    />
  );
};

const TrustScore = () => {
  const { t } = useTranslation();
  const [userProfile, setUserProfile] = useState<UserProfile | undefined>();
  const { receivedVouchers } = usePersonalVouchers();

  useEffect(() => {
    const loadUserProfile = async () => {
      const userProfile = await AccountsService.accountsProfileRetrieve();
      setUserProfile(userProfile);
    };
    loadUserProfile();
  }, []);

  const displayedValue = useMemo(() => {
    if (userProfile === undefined) return undefined;
    const { trust_score: trustScore } = userProfile;

    if (trustScore === undefined) return undefined;

    if (trustScore === null) return t('personalVouchers.trustScore.nullValue');

    if (trustScore < TRUST_SCORE_LOW) {
      return t('personalVouchers.trustScore.low');
    } else if (trustScore < TRUST_SCORE_MEDIUM) {
      return t('personalVouchers.trustScore.medium');
    } else {
      return t('personalVouchers.trustScore.high');
    }
  }, [userProfile, t]);

  const [descriptionDialogOpen, setDescriptionDialogOpen] = useState(false);

  const handleDescriptionInfoClick = useCallback(() => {
    setDescriptionDialogOpen(true);
  }, []);

  const handleDescriptionDialogClose = useCallback(() => {
    setDescriptionDialogOpen(false);
  }, []);

  return (
    <Card sx={{ width: '100%' }}>
      <CardContent sx={{ height: '100%' }}>
        <Stack gap={1} height="100%">
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
          <Box
            height="100%"
            display="flex"
            flexDirection="column"
            alignItems="center"
            justifyContent="center"
            gap={2}
          >
            <Typography
              variant="h1"
              component="span"
              fontWeight="bold"
              textTransform="uppercase"
              color={getTrustScoreColor(userProfile?.trust_score)}
            >
              {displayedValue}
            </Typography>
            <Stack gap={1}>
              <Thumb
                up={userProfile?.is_trusted}
                upDescription={t('personalVouchers.trustScore.isTrusted')}
                downDescription={t('personalVouchers.trustScore.isNotTrusted')}
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
          </Box>
        </Stack>
      </CardContent>
    </Card>
  );
};

export default TrustScore;
