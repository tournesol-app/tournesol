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
  banner: Banner;
}

const WebsiteBannerSingle = ({ banner }: WebsiteBannerSingleProps) => {
  const theme = useTheme();
  const mediaBelowXl = useMediaQuery(theme.breakpoints.down('xl'));

  return (
    <>
      {banner !== undefined && (
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
                        <strong>{banner?.title}</strong>
                      </Typography>
                    </Stack>
                    <Stack
                      direction={{ sm: 'column', md: 'row' }}
                      spacing={2}
                      alignItems="center"
                    >
                      <Typography paragraph mb={0}>
                        {banner.text}
                      </Typography>
                      <Box display="flex" justifyContent="flex-end">
                        {banner?.action_link && (
                          <Button
                            variant="contained"
                            color="primary"
                            component={Link}
                            href={banner.action_link}
                          >
                            {banner.action_label}
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
