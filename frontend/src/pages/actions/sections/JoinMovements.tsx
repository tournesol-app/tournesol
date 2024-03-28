import React from 'react';
import { Trans, useTranslation } from 'react-i18next';

import { Box, Typography } from '@mui/material';

import { ExternalLink, InternalLink } from 'src/components';
import { githubTournesolUrl } from 'src/utils/url';

const sourceCodeToContributeTo = [
  {
    text: 'CaptainFact',
    href: 'https://github.com/captainfact',
  },
  {
    text: 'Polis',
    href: 'https://github.com/compdemocracy',
  },
  {
    text: 'Tournesol',
    href: githubTournesolUrl,
  },
];

const SourceCodeToContributeTo = () => {
  const { t } = useTranslation();
  return (
    <>
      <Typography>
        {t('actionsPage.joinMovements.contributeToTheOpenSourceCodeOf')}
      </Typography>
      <ul>
        {sourceCodeToContributeTo.map((sourceCode, idx) => (
          <li key={`source_code_${idx}`}>
            <ExternalLink href={sourceCode.href}>
              {sourceCode.text}
            </ExternalLink>
          </li>
        ))}
      </ul>
    </>
  );
};

const JoinMovements = () => {
  const { t } = useTranslation();
  return (
    <Box>
      <Typography
        variant="h4"
        fontStyle="italic"
        gutterBottom
        id="join-movements"
      >
        {t('actionsPage.joinMovements.getInvolvedInDigitalDemocracyMovements')}
      </Typography>
      <ul>
        <li>
          <Typography>
            <Trans
              t={t}
              i18nKey="actionsPage.joinMovements.makeComparisonsOnTournesol"
            >
              Make <InternalLink to="/comparison">comparisons</InternalLink> on
              Tournesol.
            </Trans>
          </Typography>
        </li>
        <li>
          <Typography>
            <Trans
              t={t}
              i18nKey="actionsPage.joinMovements.takePartInFactCheckingOnCaptainFact"
            >
              Take part in{' '}
              <ExternalLink href="https://captainfact.io/videos">
                fact-checking
              </ExternalLink>{' '}
              videos on CaptainFact.
            </Trans>
          </Typography>
        </li>
        <li>
          <SourceCodeToContributeTo />
        </li>
      </ul>
    </Box>
  );
};

export default JoinMovements;
