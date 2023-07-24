import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import { Box, Divider, Stack, Button, Typography } from '@mui/material';
import Grid2 from '@mui/material/Unstable_Grid2/Grid2';

import { useCurrentPoll, useLoginState } from 'src/hooks';
import UsageStatsSection from 'src/features/statistics/UsageStatsSection';
import TitleSection from 'src/pages/home/TitleSection';
import PollListSection from 'src/pages/home/PollListSection';
import { PRESIDENTIELLE_2022_SURVEY_URL } from 'src/utils/constants';

const HomePresidentielle2022Page = () => {
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
      <Box padding={4} color="000000" bgcolor="rgba(0, 0, 0, 0.08)">
        <TitleSection title={t('home.presidentielle2022.title')}>
          <Typography paragraph>
            {t('home.presidentielle2022.tournesolDescription')}
          </Typography>
          <Typography paragraph>
            {t('home.presidentielle2022.whyCompareCandidates')}
          </Typography>
          <Typography paragraph>
            {t('home.presidentielle2022.dataUsage')}
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
            <Box width="100%">
              <Divider sx={{ my: 1 }} />
              <Typography paragraph color="#666">
                {t('home.generic.pollIsClosed')}
              </Typography>
              <Stack spacing={2} direction="row">
                <Button
                  size="large"
                  color="primary"
                  variant="contained"
                  component={Link}
                  to={`${baseUrl}/recommendations`}
                  sx={{
                    px: 4,
                    fontSize: '120%',
                  }}
                >
                  {t('home.generic.seeResults')}
                </Button>
                {isLoggedIn && (
                  <Button
                    size="large"
                    color="inherit"
                    variant="outlined"
                    sx={{
                      px: 4,
                      textAlign: 'center',
                      fontSize: '120%',
                    }}
                    href={PRESIDENTIELLE_2022_SURVEY_URL}
                  >
                    {t('home.presidentielle2022.respondToSurvey')}
                  </Button>
                )}
              </Stack>
            </Box>
          )}
        </TitleSection>
      </Box>

      <Grid2 container width="100%" flexDirection="column" alignItems="center">
        <Grid2 sx={homeSectionSx} display="flex" justifyContent="center">
          <PollListSection />
        </Grid2>
        <Grid2 sx={homeSectionSx}>
          <UsageStatsSection />
        </Grid2>
      </Grid2>
    </>
  );
};

export default HomePresidentielle2022Page;
