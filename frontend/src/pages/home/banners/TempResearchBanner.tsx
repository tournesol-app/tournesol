import React from 'react';
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

const TempResearchBanner = () => {
  const { t } = useTranslation();

  return (
    <Box py={3} bgcolor="#1282B2">
      <Grid container width="100%" flexDirection="column" alignItems="center">
        <Grid item xl={9} width="100%">
          <Paper sx={{ p: 2 }}>
            <Stack spacing={2} direction="row" alignItems="center">
              <Campaign fontSize="large" sx={{ color: '#1282B2' }} />
              <Typography paragraph>
                {t('tempResearchBanner.isTheTournesolProjectReallyEffective')}
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
                  {t('tempResearchBanner.join')}
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
