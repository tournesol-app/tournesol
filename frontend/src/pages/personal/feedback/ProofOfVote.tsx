import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { Box, TextField } from '@mui/material';

import { useCurrentPoll } from 'src/hooks';
import { UsersService } from 'src/services/openapi';

interface Props {
  keyword?: string;
  label?: string;
  helperText?: string | JSX.Element;
}

const ProofOfVote = ({
  keyword = 'proof_of_vote',
  label,
  helperText,
}: Props) => {
  const { t } = useTranslation();
  const { name: pollName } = useCurrentPoll();
  const [code, setCode] = useState('');

  useEffect(() => {
    UsersService.usersMeProofRetrieve({
      pollName: pollName,
      keyword: keyword,
    })
      .then(({ signature }) => setCode(signature))
      .catch(console.error);
  }, [keyword, pollName]);

  return (
    <Box my={2}>
      {code && (
        <TextField
          label={label ?? t('proofOfVote.proof')}
          helperText={helperText}
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
