import React from 'react';
import { Trans, useTranslation } from 'react-i18next';
import { Link as RouterLink } from 'react-router-dom';

import { Alert, Box, Link, Typography } from '@mui/material';

import { githubTournesolUrl } from 'src/utils/url';

const sourceCodeToContributeTo = [
  {
    text: 'Tournesol',
    href: githubTournesolUrl,
  },
  {
    text: 'Captain Fact',
    href: 'https://github.com/captainfact',
  },
  {
    text: 'Polis',
    href: 'https://pol.is/homehttps://github.com/compdemocracy',
  },
];

const ExternalLink = ({ text, href }: { text: string; href: string }) => {
  return (
    <Link
      href={href}
      target="_blank"
      rel="noopener"
      sx={{
        color: 'revert',
        textDecoration: 'revert',
      }}
    >
      {text}
    </Link>
  );
};

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
            <ExternalLink {...sourceCode} />
          </li>
        ))}
      </ul>
    </>
  );
};

const JoinMovements = () => {
  const { t } = useTranslation();
  return (
    <Box sx={{ '& li': { mt: 1 } }}>
      <Typography
        variant="h4"
        fontStyle="italic"
        gutterBottom
        id="join-movements"
      >
        {t('actionsPage.joinMovements.getInvolvedInDigitalDemocracyMovements')}
      </Typography>
      <Alert severity="info" icon={false}>
        {t('actionsPage.joinMovements.why')}
      </Alert>
      <ul>
        <li>
          <Typography>
            <Trans
              t={t}
              i18nKey="actionsPage.joinMovements.makeComparisonsOnTournesol"
            >
              Make{' '}
              <Link
                component={RouterLink}
                to="/comparison"
                sx={{
                  color: 'revert',
                  textDecoration: 'revert',
                }}
              >
                comparisons
              </Link>{' '}
              on Tournesol.
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
