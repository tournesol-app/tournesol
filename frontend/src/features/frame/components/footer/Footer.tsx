import React from 'react';
import { useTranslation } from 'react-i18next';

import { Box, useMediaQuery } from '@mui/material';
import Grid from '@mui/material/Unstable_Grid2';

import FooterSection from 'src/features/frame/components/footer/FooterSection';
import { getWebExtensionUrl } from 'src/utils/extension';
import {
  linkedInTournesolUrl,
  twitchTournesolUrl,
  twitterTournesolBotEnUrl,
  twitterTournesolBotFrUrl,
  twitterTournesolUrl,
  youtubePlaylistEnUrl,
  youtubePlaylistFrUrl,
  discordTournesolInviteUrl,
  githubTournesolUrl,
  KKBBTournesolEnUrl,
  KKBBTournesolFrUrl,
  paypalTournesolUrl,
  tournesolTalksMailingListUrl,
  whitePaperUrl,
} from 'src/utils/url';
import { theme } from 'src/theme';

const Footer = () => {
  const apiUrl = process.env.REACT_APP_API_URL;

  const { t, i18n } = useTranslation();
  const currentLanguage = i18n.resolvedLanguage;

  const footerSections = [
    {
      id: 'get-recommendations',
      title: t('footer.getRecommendations'),
      items: [
        {
          name: t('footer.chromeExtension'),
          to: getWebExtensionUrl('chrome') || '',
        },
        {
          name: t('footer.firefoxExtension'),
          to: getWebExtensionUrl('firefox') || '',
        },
        { name: 'Twitter Bot EN', to: twitterTournesolBotEnUrl },
        { name: 'Twitter Bot FR', to: twitterTournesolBotFrUrl },
        { name: t('footer.youtubePlaylistEn'), to: youtubePlaylistEnUrl },
        { name: t('footer.youtubePlaylistFr'), to: youtubePlaylistFrUrl },
      ],
    },
    {
      id: 'follow-us',
      title: t('footer.followUs'),
      items: [
        { name: 'Twitter', to: twitterTournesolUrl },
        { name: 'Discord', to: discordTournesolInviteUrl },
        { name: 'Twitch', to: twitchTournesolUrl },
        { name: 'LinkedIn', to: linkedInTournesolUrl },
        { name: 'GitHub', to: githubTournesolUrl },
      ],
    },
    {
      id: 'support-us',
      title: t('footer.supportUs'),
      items: [
        {
          name: t('footer.directTransfer'),
          to: '/about/donate#direct_transfer',
        },
        {
          name: 'KissKissBankBank',
          to:
            currentLanguage === 'fr' ? KKBBTournesolFrUrl : KKBBTournesolEnUrl,
        },
        { name: 'PayPal', to: paypalTournesolUrl },
        { name: t('footer.compareVideos'), to: '/comparison' },
      ],
    },
    {
      id: 'research',
      title: t('footer.research'),
      items: [
        {
          name: t('footer.whitePaper'),
          to: whitePaperUrl,
        },
        {
          name: t('footer.publicDatabase'),
          to: `${apiUrl}/exports/all/`,
        },
        /*{
          name: t('footer.tournesolTalksPage'),
          to: '/talks',
        },*/
        {
          name: t('footer.tournesolTalksMailingList'),
          to: tournesolTalksMailingListUrl,
        },
      ],
    },
    {
      id: 'more',
      title: t('footer.more'),
      items: [
        { name: t('footer.privacyPolicy'), to: '/about/privacy_policy' },
        // { name: 'FAQ', to: '' },
      ],
      trailingDivider: false,
    },
  ];

  const lessThanLargeScreen = useMediaQuery(theme.breakpoints.down('lg'), {
    noSsr: true,
  });

  return (
    <Box p={2} color="#fff" bgcolor="background.emphatic">
      <Grid
        container
        spacing={2}
        justifyContent={lessThanLargeScreen ? 'flex-start' : 'space-around'}
        alignContent="center"
      >
        {footerSections.map((section) => (
          <FooterSection
            key={section.id}
            title={section.title}
            items={section.items}
            disableItemsGutters={!lessThanLargeScreen}
            trailingDivider={section.trailingDivider}
          />
        ))}
      </Grid>
    </Box>
  );
};

export default Footer;
