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

const WebsiteBanner = ({ banner }: WebsiteBannerSingleProps) => {
  const theme = useTheme();
  const mediaBelowXl = useMediaQuery(theme.breakpoints.down('xl'));

  if (banner.title === '' || banner.text === '') {
    return <></>;
  }

  return (
    <Grid container width="100%" flexDirection="column" alignItems="center">
      <Grid item width="100%" xl={9}>
        <Paper sx={{ p: 2 }} square={mediaBelowXl}>
          <Stack direction="column" spacing={1}>
            <Stack direction="row" spacing={2} alignItems="center">
              <Campaign
                fontSize="large"
                sx={{ color: theme.palette.secondary.main }}
              />
              <Typography paragraph>
                <strong>{banner.title}</strong>
              </Typography>
            </Stack>
            <Stack
              direction={{ sm: 'column', md: 'row' }}
              spacing={{ xs: 2, sm: 2 }}
              justifyContent="space-between"
              alignItems="flex-end"
            >
              <Typography paragraph mb={0}>
                {banner.text}
              </Typography>

              {banner.action_link && banner.action_label && (
                <Box>
                  <Button
                    variant="outlined"
                    color="secondary"
                    component={Link}
                    href={banner.action_link}
                  >
                    {banner.action_label}
                  </Button>
                </Box>
              )}
            </Stack>
          </Stack>
        </Paper>
      </Grid>
    </Grid>
  );
};

export default WebsiteBanner;
