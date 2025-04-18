import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import { Box, Button, Divider, Grid2, Stack, Typography } from '@mui/material';

import WebsiteBanners from 'src/features/banners/WebsiteBanners';
import UsageStatsSection from 'src/features/statistics/UsageStatsSection';
import { useCurrentPoll, useLoginState } from 'src/hooks';
import TitleSection from 'src/pages/home/TitleSection';
import ComparisonSection from 'src/pages/home/videos/sections/ComparisonSection';
import FundingSection from 'src/pages/home/videos/sections/FundingSection';
import RecommendationsSection from 'src/pages/home/videos/sections/recommendations/RecommendationsSection';
import ResearchSection from 'src/pages/home/videos/sections/research/ResearchSection';

const HomeVideosPage = () => {
  const { t } = useTranslation();

  const { isLoggedIn } = useLoginState();
  const { baseUrl, active } = useCurrentPoll();

  const homeSectionSx = {
    width: '100%',
    padding: 6,
    px: { xs: 2, md: 6 },
  };

  return (
    <>
      <WebsiteBanners />
      <Box
        sx={{
          padding: 4,
          color: 'white',
          bgcolor: 'background.emphatic',
        }}
      >
        <TitleSection title={t('home.collaborativeContentRecommendations')}>
          <Typography
            sx={{
              fontSize: '1.1em',
              marginBottom: '16px',
            }}
          >
            {t('home.tournesolIsAParticipatoryResearchProject')}
          </Typography>

          <Typography
            sx={{
              fontSize: '1.1em',
              marginBottom: '16px',
            }}
          >
            {t('home.helpUsAdvanceResearch')}
          </Typography>

          {active ? (
            <Stack spacing={2} direction="row">
              {!isLoggedIn && (
                <Button
                  size="large"
                  color="inherit"
                  variant="outlined"
                  component={Link}
                  to={`/signup`}
                  sx={{
                    px: 4,
                    textAlign: 'center',
                    fontSize: '120%',
                  }}
                >
                  {t('home.generic.createAccount')}
                </Button>
              )}
              <Button
                size="large"
                color="primary"
                variant="contained"
                component={Link}
                to={`${baseUrl}/comparison`}
                sx={{
                  px: 4,
                  fontSize: '120%',
                }}
              >
                {t('home.generic.start')}
              </Button>
            </Stack>
          ) : (
            <Box
              sx={{
                width: '100%',
              }}
            >
              <Divider sx={{ my: 1 }} />
              <Typography
                sx={{
                  marginBottom: '16px',
                }}
              >
                {t('home.generic.pollIsClosed')}
              </Typography>
              <Stack spacing={2} direction="row">
                <Button
                  size="large"
                  color="primary"
                  variant="contained"
                  component={Link}
                  to={`${baseUrl}/search`}
                  sx={{
                    px: 4,
                    fontSize: '120%',
                  }}
                >
                  {t('home.generic.seeResults')}
                </Button>
              </Stack>
            </Box>
          )}
        </TitleSection>
      </Box>
      <Grid2
        container
        sx={{
          width: '100%',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Grid2 sx={homeSectionSx}>
          <ComparisonSection />
        </Grid2>
        <Grid2
          sx={{
            bgcolor: 'background.emphatic',
            ...homeSectionSx,
          }}
        >
          <RecommendationsSection />
        </Grid2>
        <Grid2 sx={homeSectionSx}>
          <FundingSection />
        </Grid2>
        <Grid2 sx={homeSectionSx}>
          <ResearchSection />
        </Grid2>
        <Grid2 sx={homeSectionSx}>
          <UsageStatsSection />
        </Grid2>
      </Grid2>
    </>
  );
};

export default HomeVideosPage;
