import React from 'react';

import {
  Box,
  Button,
  Grid,
  Link,
  Paper,
  Stack,
  SxProps,
  Typography,
  useMediaQuery,
  useTheme,
} from '@mui/material';
import { Campaign, Warning } from '@mui/icons-material';

import linkifyStr from 'linkify-string';

import { Banner } from 'src/services/openapi';

interface WebsiteBannerSingleProps {
  banner: Banner;
}

const securityAdvisorySx: SxProps = {
  borderWidth: '4px',
  borderStyle: 'solid',
  borderColor: 'red',
};

const WebsiteBanner = ({ banner }: WebsiteBannerSingleProps) => {
  const theme = useTheme();
  const mediaBelowXl = useMediaQuery(theme.breakpoints.down('xl'));
  const security = banner.security_advisory;

  if (banner.title === '' || banner.text === '') {
    return <></>;
  }

  let bannerSx: SxProps = { p: 2 };
  if (security) {
    bannerSx = { ...bannerSx, ...securityAdvisorySx };
  }

  const linkifyOpts = { defaultProtocol: 'https', target: '_blank' };

  return (
    <Grid
      container
      sx={{
        width: '100%',
        flexDirection: 'column',
        alignItems: 'center',
      }}
    >
      <Grid
        item
        xl={9}
        sx={{
          width: '100%',
        }}
      >
        <Paper sx={bannerSx} square={mediaBelowXl}>
          <Stack direction="column" spacing={1}>
            <Stack
              direction="row"
              spacing={2}
              sx={[
                {
                  alignItems: 'center',
                },
                security
                  ? {
                      justifyContent: 'center',
                    }
                  : {
                      justifyContent: 'flex-start',
                    },
              ]}
            >
              {security ? (
                <Warning fontSize="large" color="error" />
              ) : (
                <Campaign fontSize="large" color="secondary" />
              )}
              <Typography
                sx={{
                  marginBottom: 2,
                }}
              >
                <strong>{banner.title}</strong>
              </Typography>
              {security && <Warning fontSize="large" color="error" />}
            </Stack>
            <Box>
              <Typography
                dangerouslySetInnerHTML={{
                  __html: linkifyStr(banner.text, linkifyOpts),
                }}
                sx={{
                  display: 'inline',
                  mb: 0,
                  whiteSpace: 'pre-wrap',
                }}
              />

              {banner.action_link && banner.action_label && (
                <Button
                  variant={
                    security || (banner.priority ?? 0) >= 100
                      ? 'contained'
                      : 'outlined'
                  }
                  color={security ? 'error' : 'secondary'}
                  component={Link}
                  href={banner.action_link}
                  sx={{
                    mt: 1,
                    ml: 1,
                    float: 'right',
                  }}
                >
                  {banner.action_label}
                </Button>
              )}
            </Box>
          </Stack>
        </Paper>
      </Grid>
    </Grid>
  );
};

export default WebsiteBanner;
