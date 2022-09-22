import React from 'react';

import { Box } from '@mui/material';
import Grid from '@mui/material/Unstable_Grid2';
import FooterSection from './FooterSection';

const footerSections = [
  {
    id: 'get-recommendations',
    title: 'Get recommendations',
    items: [
      'Chrome extension',
      'Firefox extension',
      'Twitter Bot EN',
      'Twitter Bot FR',
    ],
  },
  {
    id: 'follow-us',
    title: 'Follow Us',
    items: ['Twitter', 'Discord', 'YouTube', 'Science4all'],
  },
  {
    id: 'support-us',
    title: 'Support Us',
    items: ['Direct Transfer', 'uTip', 'PayPal', 'Compare videos 🌻'],
  },
  {
    id: 'research',
    title: 'Research',
    items: ['White Paper', 'Public Dataset'],
  },
  {
    id: 'more',
    title: 'More',
    items: ['Privacy Policy', 'FAQ', 'Wiki', 'Code Source'],
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
