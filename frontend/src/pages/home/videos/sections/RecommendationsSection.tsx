import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';

import { Box, Button, IconButton, Tooltip, Typography } from '@mui/material';

import RecommendationsSubset from 'src/features/recommendation/subset/RecommendationsSubset';

import TitleSection from 'src/pages/home/TitleSection';
import {
  CampaignTwoTone,
  ExpandCircleDown,
  ExpandLess,
  ExpandMore,
} from '@mui/icons-material';

import { useAppDispatch, useAppSelector } from 'src/app/hooks';
import {
  replaceSettings,
  selectSettings,
} from 'src/features/settings/userSettingsSlice';
import { useLoginState } from 'src/hooks';
import { UsersService } from 'src/services/openapi';

const IntroHeader = () => {
  const { t } = useTranslation();
  const dispatch = useAppDispatch();
  const { isLoggedIn } = useLoginState();
  const { settings, loaded: settingsLoaded } = useAppSelector(selectSettings);
  const [btnDisabled, setBtnDisabled] = useState(false);

  // Avoid intro flickering on load
  if (isLoggedIn && !settingsLoaded) return null;

  const isIntroHidden =
    isLoggedIn && (settings?.general?.home__intro_hidden ?? false);

  const setIntroHidden = (nextHidden: boolean) => {
    setBtnDisabled(true);
    UsersService.usersMeSettingsPartialUpdate({
      requestBody: { general: { home__intro_hidden: nextHidden } },
    }).then((response) => {
      dispatch(replaceSettings(response));
      setBtnDisabled(false);
    });
  };

  if (isIntroHidden) {
    return (
      <Box
        sx={{
          position: 'relative',
          display: 'flex',
          justifyContent: 'center',
          my: 1,
        }}
      >
        <Button
          startIcon={<CampaignTwoTone />}
          color="inherit"
          variant="text"
          component={Link}
          to="/manifesto"
          sx={{ fontFamily: 'Poppins-Bold', fontSize: '1rem' }}
        >
          {t('home.readOurManifesto')}
        </Button>
        <Tooltip title={t('home.expandIntro')}>
          <IconButton
            size="small"
            disabled={btnDisabled}
            onClick={() => setIntroHidden(false)}
            sx={{
              position: 'absolute',
              top: '50%',
              right: 0,
              transform: 'translateY(-50%)',
              color: 'inherit',
              opacity: 0.6,
              '&:hover': { opacity: 1 },
            }}
          >
            <ExpandMore />
          </IconButton>
        </Tooltip>
      </Box>
    );
  }

  return (
    <Box sx={{ position: 'relative' }}>
      {isLoggedIn && (
        <Tooltip title={t('home.collapseIntro')}>
          <IconButton
            size="small"
            disabled={btnDisabled}
            onClick={() => setIntroHidden(true)}
            sx={{
              position: 'absolute',
              top: 8,
              right: 0,
              zIndex: 1,
              color: 'inherit',
              opacity: 0.6,
              '&:hover': { opacity: 1 },
            }}
          >
            <ExpandLess />
          </IconButton>
        </Tooltip>
      )}
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
    </Box>
  );
};

// A home page section that displays a subset of recommended entities.
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
      <IntroHeader />

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
