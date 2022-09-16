import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation, Trans } from 'react-i18next';

import { Box, Button, Divider, Stack, Typography } from '@mui/material';

import UsageStatsSection from 'src/features/statistics/UsageStatsSection';
import { useCurrentPoll, useLoginState } from 'src/hooks';
import ExtensionSection from 'src/pages/home/videos/ExtensionSection';
import ContributeSection from 'src/pages/home/videos/ContributeSection';
import TitleSection from 'src/pages/home/TitleSection';
import PollListSection from 'src/pages/home/PollListSection';
import AlternatingBackgroundColorSectionList from 'src/pages/home/AlternatingBackgroundColorSectionList';
import ComparisonSection from 'src/pages/home/ComparisonSection';

const HomeVideosPage = () => {
  const { t } = useTranslation();
  const { isLoggedIn } = useLoginState();
  const { baseUrl, active } = useCurrentPoll();

  return (
    <AlternatingBackgroundColorSectionList>
      <TitleSection title={t('home.collaborativeContentRecommendations')}>
        <Typography paragraph>
          <Trans t={t} i18nKey="home.tournesolPlatformDescription">
            Tournesol is an <strong>open source</strong> platform which aims to{' '}
            <strong>collaboratively</strong> identify top videos of public
            utility by eliciting contributors&apos; judgements on content
            quality. We hope to contribute to making today&apos;s and
            tomorrow&apos;s large-scale algorithms{' '}
            <strong>robustly beneficial</strong> for all of humanity.
          </Trans>
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
              to={`${baseUrl}/comparison?series=true`}
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
            <Typography paragraph>{t('home.generic.pollIsClosed')}</Typography>
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
            </Stack>
          </Box>
        )}
      </TitleSection>
      <ComparisonSection />
      <ExtensionSection />
      <ContributeSection />
      <UsageStatsSection />
      <PollListSection />
    </AlternatingBackgroundColorSectionList>
  );
};

export default HomeVideosPage;
