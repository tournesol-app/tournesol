import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Box, Divider, Stack, Button, Typography } from '@mui/material';

import TitleSection from 'src/pages/home/TitleSection';
import PollListSection from 'src/pages/home/PollListSection';
import AlternatingBackgroundColorSectionList from 'src/pages/home/AlternatingBackgroundColorSectionList';
import { useCurrentPoll, useLoginState } from 'src/hooks';

const HomePresidentielle2022Page = () => {
  const { t } = useTranslation();
  const { isLoggedIn } = useLoginState();
  const { baseUrl, active } = useCurrentPoll();

  return (
    <AlternatingBackgroundColorSectionList
      secondaryBackground="rgba(0, 0, 0, 0.08)"
      secondaryColor="#000000"
    >
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
                {t('home.presidentielle2022.createAccount')}
              </Button>
            )}
            <Button
              size="large"
              color="primary"
              variant="contained"
              component={Link}
              to={`${baseUrl}/comparison?series=true`}
              sx={{
                px: 4,
                fontSize: '120%',
              }}
            >
              {t('home.presidentielle2022.start')}
            </Button>
          </Stack>
        ) : (
          <Box width="100%">
            <Divider sx={{ my: 1 }} />
            <Typography paragraph color="#666">
              {t('home.presidentielle2022.pollIsClosed')}
            </Typography>
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
              {t('home.presidentielle2022.seeResults')}
            </Button>
          </Box>
        )}
      </TitleSection>
      <PollListSection />
      {/* 
        <UsageStatsSection /> 
        TODO: Stats are specific to videos. This component and the api 
        endpoint may be adapted to work for all Polls.
      */}
    </AlternatingBackgroundColorSectionList>
  );
};

export default HomePresidentielle2022Page;
