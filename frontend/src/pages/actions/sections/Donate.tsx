import React from 'react';
import { useTranslation } from 'react-i18next';

import { Alert, Box, Typography } from '@mui/material';

import { ExternalLink } from 'src/components';

const organisationToDonateTo = [
  {
    text: 'AlgorithmWatch',
    href: 'https://algorithmwatch.org/en/',
  },
  {
    text: 'Association Tournesol',
    href: 'https://tournesol.app/about/donate',
  },
  {
    text: 'Mozilla Foundation',
    href: 'https://foundation.mozilla.org/fr/?form=donate-header',
  },
  {
    text: 'Wikimedia France',
    href: 'https://dons.wikimedia.fr/souteneznous/~mon-don',
  },
  {
    text: 'Wikimedia Foundation',
    href: 'https://donate.wikimedia.org/wiki/Ways_to_Give',
  },
];

const OrganisationToDonateTo = () => {
  const { t } = useTranslation();
  return (
    <>
      <Typography>{t('actionsPage.donate.donateTo')}</Typography>
      <ul>
        {organisationToDonateTo.map((organisation, idx) => (
          <li key={`organisation_${idx}`}>
            <ExternalLink {...organisation} />
          </li>
        ))}
      </ul>
    </>
  );
};

const Donate = () => {
  const { t } = useTranslation();
  return (
    <Box sx={{ '& li': { mt: 1 } }}>
      <Typography variant="h4" fontStyle="italic" gutterBottom id="donate">
        {t(
          'actionsPage.donate.donateToOrganisationsFightingForQualityOfInformation'
        )}
      </Typography>
      <Box my={2}>
        <Alert severity="info" icon={false}>
          {t('actionsPage.donate.why')}
        </Alert>
      </Box>
      <OrganisationToDonateTo />
    </Box>
  );
};

export default Donate;
