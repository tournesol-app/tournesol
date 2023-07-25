import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link as RouterLink } from 'react-router-dom';

import { CircularProgress, Typography, Box, Button } from '@mui/material';

import {
  AccountsService,
  VerifyRegistration,
  VerifyEmail,
} from 'src/services/openapi';
import { ContentHeader, ContentBox } from 'src/components';
import { useCurrentPoll, useSearchParams } from 'src/hooks';
import useLastPoll from 'src/hooks/useLastPoll';
import { TRACKED_EVENTS, trackEvent } from 'src/utils/analytics';

const executeVerifyUser = async (searchParams: Record<string, string>) => {
  const { user_id, timestamp, signature } = searchParams;
  const verificationData: VerifyRegistration = {
    user_id,
    timestamp: Number(timestamp),
    signature,
  };
  return await AccountsService.accountsVerifyRegistrationCreate({
    requestBody: verificationData,
  });
};

const executeVerifyEmail = async (searchParams: Record<string, string>) => {
  const { user_id, email, timestamp, signature } = searchParams;
  const verificationData: VerifyEmail = {
    user_id,
    timestamp: Number(timestamp),
    signature,
    email,
  };
  return await AccountsService.accountsVerifyEmailCreate({
    requestBody: verificationData,
  });
};

const VerifySignature = ({ verify }: { verify: 'user' | 'email' }) => {
  useLastPoll();
  const { t } = useTranslation();
  const { baseUrl } = useCurrentPoll();
  const searchParams = useSearchParams();
  const [verificationState, setVerificationState] = useState<
    'loading' | 'fail' | 'success'
  >('loading');

  const [executeVerify, title, successMessage] =
    verify === 'user'
      ? [
          executeVerifyUser,
          t('verify.verifyRegistration'),
          `✅ ${t('verify.yourAccountIsNowVerified')}`,
        ]
      : [
          executeVerifyEmail,
          'Verify new email address',
          `✅ ${t('verify.yourNewEmailAddressIsNowVerified')}`,
        ];

  useEffect(() => {
    const verifyParams = async () => {
      try {
        await executeVerify(searchParams);
        setVerificationState('success');
        trackEvent(TRACKED_EVENTS.signup, { props: { state: 'verified' } });
      } catch (err) {
        console.error(err);
        setVerificationState('fail');
      }
    };
    verifyParams();

    // Let's make sure the verification runs only once,
    // even if searchParams are re-evaluated.
    //
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <>
      <ContentHeader title={title} />
      <ContentBox maxWidth="sm">
        <Typography paragraph>
          {verificationState == 'loading' && <CircularProgress />}
          {verificationState == 'fail' && t('verify.verificationFailed')}
          {verificationState == 'success' && successMessage}
        </Typography>
        {verify === 'user' && verificationState === 'success' && (
          <Box display="flex" justifyContent="center">
            <Button
              component={RouterLink}
              to={`${baseUrl}/comparison`}
              variant="contained"
              color="primary"
            >
              {t('home.compareButton')}
            </Button>
          </Box>
        )}
      </ContentBox>
    </>
  );
};

export default VerifySignature;
