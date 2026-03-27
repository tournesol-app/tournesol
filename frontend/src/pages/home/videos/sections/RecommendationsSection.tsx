import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';

import { Box, Button, Typography } from '@mui/material';

import RecommendationsSubset from 'src/features/recommendation/subset/RecommendationsSubset';
import { useAppDispatch, useAppSelector } from 'src/app/hooks';
import {
  replaceSettings,
  selectSettings,
} from 'src/features/settings/userSettingsSlice';
import { useLoginState } from 'src/hooks';
import { UsersService } from 'src/services/openapi';

import TitleSection from 'src/pages/home/TitleSection';
import { CampaignTwoTone, ExpandCircleDown } from '@mui/icons-material';

const anonymousIntroStorageKey = 'home.introHidden';

const getIntroStorageKey = (username?: string) => {
  return username
    ? `${anonymousIntroStorageKey}:${username}`
    : anonymousIntroStorageKey;
};

const readStoredIntroHidden = (username?: string) => {
  if (typeof window === 'undefined') {
    return false;
  }

  try {
    return window.localStorage.getItem(getIntroStorageKey(username)) === '1';
  } catch {
    return false;
  }
};

const writeStoredIntroHidden = (isHidden: boolean, username?: string) => {
  if (typeof window === 'undefined') {
    return;
  }

  try {
    window.localStorage.setItem(
      getIntroStorageKey(username),
      isHidden ? '1' : '0'
    );
  } catch {
    // Ignore.
  }
};

/**
 * A home page section that displays a subset of recommended entities.
 */
const RecommendationsSection = () => {
  const { i18n, t } = useTranslation();
  const dispatch = useAppDispatch();
  const { isLoggedIn, loginState } = useLoginState();

  const currentLang = i18n.resolvedLanguage || i18n.language;
  const userSettings = useAppSelector(selectSettings).settings;
  const accountIntroHidden = userSettings?.general?.home__intro_hidden;
  const username = loginState.username;

  // Determine the date filter applied when the user click on the see more
  // button.
  const [seeMoreDate, setSeeMoreDate] = useState('Month');
  const onRecoDateChangeCallback = (selectedDate: string) => {
    setSeeMoreDate(selectedDate);
  };

  const [isIntroHidden, setIsIntroHidden] = useState(false);
  useEffect(() => {
    if (accountIntroHidden !== undefined) {
      setIsIntroHidden(accountIntroHidden);
      if (username) {
        writeStoredIntroHidden(accountIntroHidden, username);
      }
      return;
    }

    if (!isLoggedIn) {
      setIsIntroHidden(readStoredIntroHidden());
      return;
    }

    if (username) {
      setIsIntroHidden(readStoredIntroHidden(username));
      return;
    }

    setIsIntroHidden(false);
  }, [accountIntroHidden, isLoggedIn, username]);

  const setIntroHidden = async (nextHidden: boolean) => {
    const previousHidden = isIntroHidden;

    setIsIntroHidden(nextHidden);
    if (isLoggedIn) {
      if (username) {
        writeStoredIntroHidden(nextHidden, username);
      }
    } else {
      writeStoredIntroHidden(nextHidden);
    }

    if (!isLoggedIn) {
      return;
    }

    try {
      const response = await UsersService.usersMeSettingsPartialUpdate({
        requestBody: {
          general: {
            home__intro_hidden: nextHidden,
          },
        },
      });
      dispatch(replaceSettings(response));
    } catch {
      setIsIntroHidden(previousHidden);
      if (username) {
        writeStoredIntroHidden(previousHidden, username);
      }
    }
  };

  return (
    <>
      {!isIntroHidden && (
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

          <Box
            sx={{
              display: 'flex',
              flexWrap: 'wrap',
              gap: 1.5,
              alignItems: 'center',
              marginBottom: 2,
            }}
          >
            <Button
              startIcon={<CampaignTwoTone />}
              color="primary"
              variant="contained"
              component={Link}
              to={`/manifesto`}
              sx={{
                px: 4,
                fontSize: '110%',
              }}
            >
              {t('home.readOurManifesto')}
            </Button>
            <Button
              variant="contained"
              disableElevation
              onClick={() => setIntroHidden(true)}
              sx={(theme) => ({
                px: 4,
                fontSize: '110%',
                color: '#FFFFFF',
                bgcolor: 'rgba(255, 255, 255, 0.12)',
                border: '1px solid rgba(255, 255, 255, 0.24)',
                boxShadow: 'none',
                backdropFilter: 'blur(8px)',
                alignSelf: 'flex-start',
                '&:hover': {
                  bgcolor: 'rgba(255, 255, 255, 0.18)',
                  borderColor: 'rgba(255, 255, 255, 0.34)',
                  boxShadow: 'none',
                },
                '&:focus-visible': {
                  outline: `2px solid ${theme.palette.primary.main}`,
                  outlineOffset: 2,
                },
              })}
            >
              {t('home.hideIntro')}
            </Button>
          </Box>
        </TitleSection>
      )}

      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          flexDirection: 'column',
          gap: 1,
          mt: isIntroHidden ? { xs: 2, md: 3 } : 0,
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
