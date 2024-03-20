import React from 'react';
import { Trans, useTranslation } from 'react-i18next';

import { Alert, Box, Link, Typography } from '@mui/material';

import { ExternalLink } from 'src/components';

const projectsToPromote = [
  {
    text: 'Tournesol',
    href: 'https://tournesol.app',
  },
  {
    text: 'Algorithmic Personalization Project',
    href: 'https://personalization.csail.mit.edu',
  },
  {
    text: 'Horus',
    href: 'https://iscpif.fr/horus-methodologie/',
  },
  {
    text: 'Politoscope',
    href: 'https://politoscope.org',
  },
  {
    text: 'TheirTube',
    href: 'https://www.their.tube',
  },
];

const ProjectsToPromote = () => {
  const { t } = useTranslation();
  return (
    <>
      <Typography>
        {t('actionsPage.helpResearch.promoteAndTakePartInProjectsLike')}
      </Typography>
      <ul>
        {projectsToPromote.map((project, idx) => (
          <li key={`projects_to_promote_${idx}`}>
            <ExternalLink {...project} />
          </li>
        ))}
      </ul>
    </>
  );
};

const HelpResearch = () => {
  const { t } = useTranslation();
  return (
    <Box sx={{ '& li': { mt: 1 } }}>
      <Typography
        variant="h4"
        fontStyle="italic"
        gutterBottom
        id="help-research"
      >
        {t(
          'actionsPage.helpResearch.helpScientificResearchThatServesPublicInterest'
        )}
      </Typography>
      <Box my={2}>
        <Alert severity="info" icon={false}>
          {t('actionsPage.helpResearch.why')}
        </Alert>
      </Box>
      <ul>
        <li>
          <ProjectsToPromote />
        </li>
        <li>
          <Trans t={t} i18nKey="actionsPage.helpResearch.attendTournesolTalks">
            Attend to{' '}
            <Link
              href="https://tournesol.app/talks"
              target="_blank"
              rel="noopener"
              sx={{
                color: 'revert',
                textDecoration: 'revert',
              }}
            >
              Tournesol Talks
            </Link>
            , or{' '}
            <Link
              // xxx set the correct contact address
              href="https://tournesol.app"
              target="_blank"
              rel="noopener"
              sx={{
                color: 'revert',
                textDecoration: 'revert',
              }}
            >
              ask to intervene
            </Link>
            .
          </Trans>
        </li>
      </ul>
    </Box>
  );
};

export default HelpResearch;
