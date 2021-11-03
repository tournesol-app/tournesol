import React, { useEffect, useState } from 'react';
import { CircularProgress, Typography } from '@material-ui/core';
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
  return await AccountsService.accountsVerifyRegistrationCreate(
    verificationData
  );
};

const executeVerifyEmail = async (searchParams: Record<string, string>) => {
  const { user_id, email, timestamp, signature } = searchParams;
  const verificationData: VerifyEmail = {
    user_id,
    timestamp: Number(timestamp),
    signature,
    email,
  };
  return await AccountsService.accountsVerifyEmailCreate(verificationData);
};

const VerifySignature = ({ verify }: { verify: 'user' | 'email' }) => {
  const searchParams = useSearchParams();
  const [verificationState, setVerificationState] = useState<
    'loading' | 'fail' | 'success'
  >('loading');

  useEffect(() => {
    const verifyParams = async () => {
      try {
        if (verify === 'user') {
          await executeVerifyUser(searchParams);
        } else if (verify === 'email') {
          await executeVerifyEmail(searchParams);
        }
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

  const title =
    verify === 'user' ? 'Verify registration' : 'Verify new email address';

  const successMessage =
    verify === 'user'
      ? '✅ Your account is now verified.'
      : '✅ Your new email address is now verified.';

  return (
    <>
      <ContentHeader title={title} />
      <ContentBox maxWidth="sm">
        <Typography>
          {verificationState == 'loading' && <CircularProgress />}
          {verificationState == 'fail' && 'Verification failed.'}
          {verificationState == 'success' && successMessage}
        </Typography>
      </ContentBox>
    </>
  );
};

export default VerifySignature;
