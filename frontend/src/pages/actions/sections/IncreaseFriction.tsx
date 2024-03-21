import React from 'react';
import { Trans, useTranslation } from 'react-i18next';

import { Box, Link, Typography } from '@mui/material';
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
    <Box>
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
        <li>
          <Trans
            t={t}
            i18nKey="actionsPage.increaseFriction.findOutAboutAndApplyOtherStrategies"
          >
            Find out about and apply other strategies, such as those from the
            article{' '}
            <Link
              href="https://www.humanetech.com/take-control"
              target="_blank"
              rel="noopener"
              sx={{
                color: 'revert',
                textDecoration: 'revert',
              }}
            >
              Control Your Tech Use
            </Link>
            .
          </Trans>
        </li>
        <li>{t('actionsPage.increaseFriction.takeRegularInternetBreaks')}</li>
        <li>{t('actionsPage.increaseFriction.organizeYourEnvironment')}</li>
      </ul>
    </Box>
  );
};

export default IncreaseFriction;
