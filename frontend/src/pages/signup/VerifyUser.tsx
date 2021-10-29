import React, { useEffect, useState } from 'react';
import { Typography } from '@material-ui/core';
import { AccountsService, VerifyRegistration } from 'src/services/openapi';
import { ContentHeader, ContentBox } from 'src/components';
import { useSearchParams } from 'src/hooks';

function VerifyUser() {
  const searchParams = useSearchParams();
  const [verificationState, setVerificationState] = useState<
    'loading' | 'fail' | 'success'
  >('loading');

  useEffect(() => {
    const verifyParams = async () => {
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

    // Let's make sure the verification runs only once,
    // even if searchParams are re-evaluated.
    //
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

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
