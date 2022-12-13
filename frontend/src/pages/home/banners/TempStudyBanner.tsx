import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import {
  Box,
  Button,
  Grid,
  Link,
  Paper,
  Stack,
  Typography,
} from '@mui/material';
import { Biotech, Campaign } from '@mui/icons-material';

import { useCurrentPoll } from 'src/hooks';
import { UsersService } from 'src/services/openapi';

// TODO: these values are placeholder values that will be updated.
const STUDY_DATE_START = new Date('2022-01-01T00:00:00Z');
const STUDY_DATE_END = new Date('2024-01-01T00:00:00Z');

const TempStudyBanner = () => {
  const { t } = useTranslation();
  const { name: pollName } = useCurrentPoll();

  const [proofOfVote, setProofOfVote] = useState('');

  const now = new Date();

  useEffect(() => {
    if (now < STUDY_DATE_START || now > STUDY_DATE_END) {
      return;
    }

    UsersService.usersMeProofOfVotesRetrieve({ pollName })
      .then(({ signature }) => setProofOfVote(signature))
      .catch(console.error);

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pollName]);

  if (now < STUDY_DATE_START || now > STUDY_DATE_END) {
    return <></>;
  }

  return (
    <Box py={3} bgcolor="#1282B2">
      <Grid container width="100%" flexDirection="column" alignItems="center">
        <Grid item xl={9} width="100%">
          <Paper sx={{ p: 2 }}>
            <Stack spacing={2} direction="row" alignItems="center">
              <Campaign fontSize="large" sx={{ color: '#1282B2' }} />
              <Typography paragraph>
                {t('tempStudyBanner.isTheTournesolProjectReallyEffective')}
              </Typography>
              <Box display="flex" justifyContent="center">
                <Button
                  variant="contained"
                  component={Link}
                  target="_blank"
                  rel="noopener"
                  href={`https://tournesol.app?proof=${proofOfVote}`}
                  endIcon={<Biotech />}
                >
                  {t('tempStudyBanner.join')}
                </Button>
              </Box>
            </Stack>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default TempStudyBanner;
