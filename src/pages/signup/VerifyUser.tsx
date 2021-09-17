import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router';
import { Typography } from '@material-ui/core';
import { AccountsService, VerifyRegistration } from 'src/services/openapi';
import { ContentHeader, ContentBox } from 'src/components';

function VerifyUser() {
  const location = useLocation();
  const [verificationState, setVerificationState] = useState<
    'loading' | 'fail' | 'success'
  >('loading');

  useEffect(() => {
    const verifyParams = async () => {
      const searchParams = Object.fromEntries(
        new URLSearchParams(location.search)
      );
      const { user_id, timestamp, signature } = searchParams;
      const verificationData: VerifyRegistration = {
        user_id,
        timestamp: Number(timestamp),
        signature,
      };
      try {
        await AccountsService.accountsVerifyRegistrationCreate(
          verificationData
        );
        setVerificationState('success');
      } catch (err) {
        console.error(err);
        setVerificationState('fail');
      }
    };
    verifyParams();
  }, [location.search]);

  return (
    <>
      <ContentHeader title="Verify registration" />
      <ContentBox maxWidth="sm">
        <Typography>
          {verificationState == 'loading' && 'Loading...'}
          {verificationState == 'fail' && 'Verification failed.'}
          {verificationState == 'success' && '✅ Your account is now verified.'}
        </Typography>
      </ContentBox>
    </>
  );
}

export default VerifyUser;
