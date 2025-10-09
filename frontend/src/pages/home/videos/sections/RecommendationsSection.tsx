import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';

import { Box, Button, Typography } from '@mui/material';

import RecommendationsSubset from 'src/features/recommendation/subset/RecommendationsSubset';

import TitleSection from 'src/pages/home/TitleSection';
import { CampaignTwoTone, ExpandCircleDown } from '@mui/icons-material';

/**
 * A home page section that displays a subset of recommended entities.
 */
const RecommendationsSection = () => {
  const { i18n, t } = useTranslation();

  const currentLang = i18n.resolvedLanguage || i18n.language;

  // Determine the date filter applied when the user click on the see more
  // button.
  const [seeMoreDate, setSeeMoreDate] = useState('Month');
  const onRecoDateChangeCallback = (selectedDate: string) => {
    setSeeMoreDate(selectedDate);
  };

  return (
    <>
      <TitleSection title={t('home.collaborativeContentRecommendations')}>
        <Typography
          sx={{
            fontSize: '1.1em',
            marginBottom: 2,
          }}
        >
          {t('home.tournesolIsAParticipatoryResearchProject')}
        </Typography>
        <Typography
          sx={{
            fontSize: '1.1em',
            marginBottom: 2,
          }}
        >
          {t('recommendationsSection.eachComparisonHelps')}
        </Typography>

        <Button
          startIcon={<CampaignTwoTone />}
          color="primary"
          variant="contained"
          component={Link}
          to={`/manifesto`}
          sx={{
            px: 4,
            fontSize: '110%',
            marginBottom: 2,
          }}
        >
          {t('home.readOurManifesto')}
        </Button>
      </TitleSection>

      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          flexDirection: 'column',
          gap: 1,
          mb: 4,
        }}
      >
        <RecommendationsSubset
          language={currentLang}
          displayControls
          onRecoDateChange={onRecoDateChangeCallback}
        />
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'center',
          }}
        >
          <Button
            fullWidth
            color="secondary"
            startIcon={<ExpandCircleDown />}
            component={Link}
            to={`/search?date=${seeMoreDate}&language=${currentLang}`}
            sx={(t) => ({ bgcolor: t.palette.background.paper })}
          >
            {t('recommendationsSection.seeMore')}
          </Button>
        </Box>
      </Box>
    </>
  );
};

export default RecommendationsSection;
