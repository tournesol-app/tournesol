import React from 'react';

import { Box } from '@mui/material';
import Grid from '@mui/material/Unstable_Grid2';
import FooterSection from './FooterSection';

const footerSections = [
  {
    id: 'get-recommendations',
    title: 'Get recommendations',
    items: [
      {
        name: 'Chrome extension',
        to: 'https://chrome.google.com/webstore/detail/tournesol-extension/nidimbejmadpggdgooppinedbggeacla',
      },
      {
        name: 'Firefox extension',
        to: 'https://addons.mozilla.org/fr/firefox/addon/tournesol-extension/',
      },
      { name: 'Twitter Bot EN', to: 'https://twitter.com/tournesolbotfr' },
      { name: 'Twitter Bot FR', to: 'https://twitter.com/tournesolbot' },
    ],
  },
  {
    id: 'follow-us',
    title: 'Follow Us',
    items: [
      { name: 'Twitter', to: 'https://twitter.com/TournesolApp' },
      { name: 'Discord', to: 'https://discord.gg/TvsFB8RNBV' },
      {
        name: 'YouTube',
        to: 'https://www.youtube.com/channel/UCH8TsmKEX_PR4jxsg2W3vOg',
      },
      {
        name: 'Science4all',
        to: 'https://www.youtube.com/c/Science4Allfran%C3%A7ais',
      },
    ],
  },
  {
    id: 'support-us',
    title: 'Support Us',
    items: [
      { name: 'Direct Transfer', to: '/about/donate' },
      { name: 'uTip', to: 'https://utip.io/tournesol' },
      { name: 'PayPal', to: 'https://www.paypal.com/paypalme/tournesolapp' },
      { name: 'Compare videos 🌻', to: '/comparison' },
    ],
  },
  {
    id: 'research',
    title: 'Research',
    items: [
      { name: 'White Paper', to: 'https://arxiv.org/abs/2107.07334' },
      { name: 'Public Dataset', to: '' },
    ],
  },
  {
    id: 'more',
    title: 'More',
    items: [
      { name: 'Privacy Policy', to: '/about/privacy_policy' },
      // { name: 'FAQ', to: '' },
      { name: 'Wiki', to: 'https://wiki.tournesol.app/' },
      { name: 'Code Source', to: 'https://github.com/tournesol-app/tournesol' },
    ],
  },
];

const Footer = () => {
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
          />
        ))}
      </Grid>
    </Box>
  );
};

export default Footer;
