import React from 'react';

import {
  Box,
  Button,
  Grid,
  Link,
  Paper,
  Stack,
  Typography,
  useMediaQuery,
  useTheme,
} from '@mui/material';
import { Campaign } from '@mui/icons-material';

import { Banner } from 'src/services/openapi';

interface WebsiteBannerSingleProps {
  banners: Array<Banner>;
}

const WebsiteBannerSingle = ({ banners }: WebsiteBannerSingleProps) => {
  const theme = useTheme();
  const mediaBelowXl = useMediaQuery(theme.breakpoints.down('xl'));

  return (
    <>
      {banners[0] !== undefined && (
        <Box py={3} bgcolor="#1282B2">
          <Grid
            container
            width="100%"
            flexDirection="column"
            alignItems="center"
          >
            <Grid item xl={9} width="100%" spacing={2} direction="column">
              <Paper sx={{ p: 2 }} square={mediaBelowXl}>
                <Stack
                  // Using != direction per breakpoint requires to define != spacing
                  // per breakpoint.
                  spacing={{ xs: 2, sm: 2 }}
                  direction={{ sm: 'column', md: 'row' }}
                  alignItems="center"
                  justifyContent="space-between"
                >
                  <Stack direction="column" spacing={2}>
                    <Stack direction="row" spacing={2} alignItems="center">
                      <Campaign fontSize="large" sx={{ color: '#1282B2' }} />
                      <Typography paragraph>
                        <strong>{banners[0]?.title}</strong>
                      </Typography>
                    </Stack>
                    <Stack
                      direction={{ sm: 'column', md: 'row' }}
                      spacing={2}
                      alignItems="center"
                    >
                      <Typography paragraph mb={0}>
                        {banners[0].text}
                      </Typography>
                      <Box display="flex" justifyContent="flex-end">
                        {banners[0]?.action_link && (
                          <Button
                            variant="contained"
                            color="primary"
                            component={Link}
                            href={banners[0].action_link}
                          >
                            {banners[0].action_label}
                          </Button>
                        )}
                      </Box>
                    </Stack>
                  </Stack>
                </Stack>
              </Paper>
            </Grid>
          </Grid>
        </Box>
      )}
    </>
  );
};

export default WebsiteBannerSingle;
