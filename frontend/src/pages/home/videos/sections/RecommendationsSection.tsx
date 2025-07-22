import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';

import { Box, Button, Grid, Typography } from '@mui/material';

import RecommendationsSubset from 'src/features/recommendation/subset/RecommendationsSubset';

import TitleSection from 'src/pages/home/TitleSection';

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
      </TitleSection>

      <Grid
        container
        sx={{
          justifyContent: 'center',
          pb: 4,
        }}
      >
        <Grid item lg={9}>
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'center',
              flexDirection: 'column',
              gap: 2,
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
                variant="contained"
                component={Link}
                to={`/search?date=${seeMoreDate}&language=${currentLang}`}
              >
                {t('recommendationsSection.seeMore')}
              </Button>
            </Box>
          </Box>
        </Grid>
      </Grid>
    </>
  );
};

export default RecommendationsSection;
