import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { CircularProgress, Typography } from '@mui/material';
import {
  AccountsService,
  VerifyRegistration,
  VerifyEmail,
} from 'src/services/openapi';
import { ContentHeader, ContentBox } from 'src/components';
import { useSearchParams } from 'src/hooks';

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
  const { t } = useTranslation();
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
        <Typography>
          {verificationState == 'loading' && <CircularProgress />}
          {verificationState == 'fail' && t('verify.verificationFailed')}
          {verificationState == 'success' && successMessage}
        </Typography>
      </ContentBox>
    </>
  );
};

export default VerifySignature;
