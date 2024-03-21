import React from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Typography } from '@mui/material';
import { ExternalLink } from 'src/components';

const appsToInstall = [
  {
    text: 'Forest',
    href: 'https://www.forestapp.cc',
  },
  {
    text: 'Focus Lock',
    href: 'https://apps.apple.com/us/app/focus-lock-block-apps-focus/id1494966346',
  },
  {
    text: 'Cold Turkey',
    href: 'https://getcoldturkey.com',
  },
];

const AppsToInstall = () => {
  const { t } = useTranslation();
  return (
    <>
      <Typography>
        {t('actionsPage.increaseFriction.installApplications')}
      </Typography>
      <ul>
        {appsToInstall.map((sourceCode, idx) => (
          <li key={`source_code_${idx}`}>
            <ExternalLink {...sourceCode} />
          </li>
        ))}
      </ul>
    </>
  );
};

const IncreaseFriction = () => {
  const { t } = useTranslation();
  return (
    <Box sx={{ '& li': { mt: 1 } }}>
      <Typography
        variant="h4"
        fontStyle="italic"
        gutterBottom
        id="increase-friction"
      >
        {t(
          'actionsPage.increaseFriction.increaseFrictionBetweenYouAndUndesirableInformationUsage'
        )}
      </Typography>
      <ul>
        <li>
          {t('actionsPage.increaseFriction.deleteSocialMediaFromYourPhones')}
        </li>
        <li>
          <AppsToInstall />
        </li>
      </ul>
    </Box>
  );
};

export default IncreaseFriction;
