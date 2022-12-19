import React, { useEffect, useState } from 'react';
import { useTranslation, Trans } from 'react-i18next';
import { Box, TextField } from '@mui/material';
import { UsersService } from 'src/services/openapi';
import { useCurrentPoll } from 'src/hooks';
import { PRESIDENTIELLE_2022_SURVEY_URL } from 'src/utils/constants';

const ProofOfVote = () => {
  const { t } = useTranslation();
  const { name: pollName } = useCurrentPoll();
  const [code, setCode] = useState('');

  useEffect(() => {
    UsersService.usersMeProofRetrieve({
      pollName: pollName,
      keyword: 'proof_of_vote',
    })
      .then(({ signature }) => setCode(signature))
      .catch(console.error);
  }, [pollName]);

  const codeHelperText = (
    <Trans t={t} i18nKey="myFeedbackPage.proofOfVoteHelperText">
      This code will be helpful to complete{' '}
      <a target="_blank" rel="noreferrer" href={PRESIDENTIELLE_2022_SURVEY_URL}>
        our survey.
      </a>
    </Trans>
  );

  return (
    <Box my={2}>
      {code && (
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
      )}
    </Box>
  );
};

export default ProofOfVote;
