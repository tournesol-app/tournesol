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
  const bannerParagraphs = linkifyStr(banner.text, linkifyOpts).split('\n');

  return (
    <Grid container width="100%" flexDirection="column" alignItems="center">
      <Grid item width="100%" xl={9}>
        <Paper sx={bannerSx} square={mediaBelowXl}>
          <Stack direction="column" spacing={1}>
            <Stack
              direction="row"
              spacing={2}
              alignItems="center"
              justifyContent={security ? 'center' : 'flex-start'}
            >
              {security ? (
                <Warning fontSize="large" color="error" />
              ) : (
                <Campaign fontSize="large" color="secondary" />
              )}
              <Typography paragraph>
                <strong>{banner.title}</strong>
              </Typography>
              {security && <Warning fontSize="large" color="error" />}
            </Stack>
            <Stack
              direction={{ sm: 'column', md: 'row' }}
              spacing={{ xs: 2, sm: 2 }}
              justifyContent="space-between"
              alignItems="flex-end"
            >
              <Box>
                {bannerParagraphs.map((paragraph, index) => (
                  <Typography
                    paragraph
                    key={`banner_p${index}`}
                    mb={index + 1 === bannerParagraphs.length ? 0 : 2}
                    dangerouslySetInnerHTML={{ __html: paragraph }}
                  />
                ))}
              </Box>

              {banner.action_link && banner.action_label && (
                <Box minWidth="100px">
                  <Button
                    variant={
                      security || (banner.priority ?? 0) >= 100
                        ? 'contained'
                        : 'outlined'
                    }
                    color={security ? 'error' : 'secondary'}
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
