import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Box, TextField } from '@mui/material';
import { UsersService } from 'src/services/openapi';
import { useCurrentPoll } from 'src/hooks';

const ProofOfVote = () => {
  const { t } = useTranslation();
  const { name: pollName } = useCurrentPoll();
  const [code, setCode] = useState('');

  useEffect(() => {
    UsersService.usersMeProofOfVotesRetrieve({ pollName })
      .then(({ signature }) => setCode(signature))
      .catch(console.error);
  }, [pollName]);

  const codeHelperText = (
    <span>
      {t('myFeedbackPage.proofOfVoteHelperText')}{' '}
      {/* TODO add link to survey:
       <a target="_blank" href={'https://tournesol.app'} rel="noreferrer">
        https://tournesol.app
      </a> */}
    </span>
  );

  return (
    <Box my={2}>
      {code && (
        <>
          <TextField
            label={t('myFeedbackPage.proofOfVote')}
            helperText={codeHelperText}
            color="secondary"
            fullWidth
            value={code}
            InputProps={{
              readOnly: true,
              sx: {
                bgcolor: 'white',
                fontFamily: 'monospace',
              },
            }}
            onFocus={(e) => e.target.select()}
          />
        </>
      )}
    </Box>
  );
};

export default ProofOfVote;
