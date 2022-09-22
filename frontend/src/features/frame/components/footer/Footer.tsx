import React from 'react';
import { useTranslation } from 'react-i18next';

import { Box } from '@mui/material';
import Grid from '@mui/material/Unstable_Grid2';

import FooterSection from 'src/features/frame/components/footer/FooterSection';
import { getWebExtensionUrl } from 'src/utils/extension';
import { getWikiBaseUrl } from 'src/utils/url';

const Footer = () => {
  const apiUrl = process.env.REACT_APP_API_URL;

  const { t } = useTranslation();

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
        { name: 'Twitter Bot EN', to: 'https://twitter.com/tournesolbotfr' },
        { name: 'Twitter Bot FR', to: 'https://twitter.com/tournesolbot' },
      ],
    },
    {
      id: 'follow-us',
      title: t('footer.followUs'),
      items: [
        { name: 'Twitter', to: 'https://twitter.com/TournesolApp' },
        { name: 'Discord', to: 'https://discord.gg/TvsFB8RNBV' },
        {
          name: 'YouTube',
          to: 'https://www.youtube.com/channel/UCH8TsmKEX_PR4jxsg2W3vOg',
        },
        {
          name: 'GitHub',
          to: 'https://github.com/tournesol-app/tournesol',
        },
      ],
    },
    {
      id: 'support-us',
      title: t('footer.supportUs'),
      items: [
        { name: t('footer.directTransfer'), to: '/about/donate' },
        { name: 'uTip', to: 'https://utip.io/tournesol' },
        { name: 'PayPal', to: 'https://www.paypal.com/paypalme/tournesolapp' },
        { name: t('footer.compareVideos'), to: '/comparison' },
      ],
    },
    {
      id: 'research',
      title: t('footer.research'),
      items: [
        {
          name: t('footer.whitePaper'),
          to: 'https://arxiv.org/abs/2107.07334',
        },
        {
          name: t('footer.publicDataset'),
          to: `${apiUrl}/exports/comparisons/`,
        },
      ],
    },
    {
      id: 'more',
      title: t('footer.more'),
      items: [
        { name: t('footer.privacyPolicy'), to: '/about/privacy_policy' },
        // { name: 'FAQ', to: '' },
        { name: 'Wiki', to: getWikiBaseUrl() },
      ],
      trailingDivider: false,
    },
  ];

  return (
    <Box padding={2} color="#fff" bgcolor="#1282B2">
      <Grid
        container
        spacing={2}
        justifyContent="space-around"
        alignContent="center"
      >
        {footerSections.map((section) => (
          <FooterSection
            key={section.id}
            title={section.title}
            items={section.items}
            trailingDivider={section.trailingDivider}
          />
        ))}
      </Grid>
    </Box>
  );
};

export default Footer;
