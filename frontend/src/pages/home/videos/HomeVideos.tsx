import React from 'react';
import { useTranslation, Trans } from 'react-i18next';
import { Typography } from '@mui/material';
//import { Button } from '@mui/material';

//import { Link } from 'react-router-dom';
import UsageStatsSection from 'src/features/statistics/UsageStatsSection';
import ExtensionSection from 'src/pages/home/videos/ExtensionSection';
import ContributeSection from 'src/pages/home/videos/ContributeSection';
import TitleSection from 'src/pages/home/TitleSection';
import PollListSection from 'src/pages/home/PollListSection';
import AlternatingBackgroundColorSectionList from 'src/pages/home/AlternatingBackgroundColorSectionList';

const HomeVideosPage = () => {
  const { t } = useTranslation();

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
        {/*<Button
          color="primary"
          variant="contained"
          component={Link}
          to="/comparison?series=true"
        >
          {t('home.videos.start')}
        </Button>*/}
      </TitleSection>
      <ExtensionSection />
      <ContributeSection />
      <PollListSection />
      <UsageStatsSection />
    </AlternatingBackgroundColorSectionList>
  );
};

export default HomeVideosPage;
