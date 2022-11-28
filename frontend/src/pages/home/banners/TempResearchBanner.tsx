import React from 'react';

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

const TempResearchBanner = () => {
  return (
    <Box py={3} bgcolor="#1282B2">
      <Grid container width="100%" flexDirection="column" alignItems="center">
        <Grid item xl={9} width="100%">
          <Paper sx={{ p: 2 }}>
            <Stack spacing={2} direction="row" alignItems="center">
              <Campaign fontSize="large" sx={{ color: '#1282B2' }} />
              <Typography paragraph>
                Is the Tournesol project really effective? We are currently
                investigating the impact of the Tournesol browser extension on
                the YouTube viewers&apos; habits. Join our research study to
                help us improve Tournesol!
              </Typography>
              <Box display="flex" justifyContent="center">
                <Button
                  variant="contained"
                  component={Link}
                  target="_blank"
                  rel="noopener"
                  href="https://tournesol.app"
                  endIcon={<Biotech />}
                >
                  Join
                </Button>
              </Box>
            </Stack>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default TempResearchBanner;
