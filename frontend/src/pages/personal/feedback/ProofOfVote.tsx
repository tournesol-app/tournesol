import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { Box, IconButton, InputAdornment, TextField } from '@mui/material';
import { Check, ContentCopy } from '@mui/icons-material';

import { useCurrentPoll } from 'src/hooks';
import { UsersService } from 'src/services/openapi';

// in milliseconds
const FEEDBACK_DELAY = 1200;

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
  const [feedback, setFeedback] = useState(false);

  const copyToClipboard = () => {
    navigator.clipboard.writeText(code);

    // Do not trigger any additionnal rendering when the user clicks
    // repeatedly on the button.
    if (feedback) {
      return;
    }

    setFeedback(true);

    setTimeout(() => {
      setFeedback(false);
    }, FEEDBACK_DELAY);
  };

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
            endAdornment: (
              <InputAdornment position="end">
                <IconButton
                  aria-label={t('proofOfVote.copyTheProof')}
                  edge="end"
                  onClick={copyToClipboard}
                >
                  {feedback ? <Check /> : <ContentCopy />}
                </IconButton>
              </InputAdornment>
            ),
          }}
          onFocus={(e) => e.target.select()}
        />
      )}
    </Box>
  );
};

export default ProofOfVote;
