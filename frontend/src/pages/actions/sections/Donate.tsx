import React from 'react';
import { useTranslation } from 'react-i18next';

import { Alert, Box, Typography } from '@mui/material';

import { ExternalLink } from 'src/components';

interface Organization {
  name: string;
  href: string;
  desc: string;
}

const OrganisationToDonateTo = ({
  organizations,
}: {
  organizations: Organization[];
}) => {
  return (
    <>
      {organizations.map((organisation, idx) => (
        <Box key={`organisation_${idx}`}>
          <Box display="flex" gap={1}>
            <Typography variant="h6" gutterBottom>
              {organisation.name}
            </Typography>
            <ExternalLink
              key={`organisation_${idx}`}
              text={organisation.href}
              href={organisation.href}
            />
          </Box>
          <Typography paragraph>{organisation.desc}</Typography>
        </Box>
      ))}
    </>
  );
};

const Donate = () => {
  const { t } = useTranslation();

  const organizations = [
    {
      name: 'AlgorithmWatch',
      href: 'https://algorithmwatch.org/en/donate/',
      desc: t('actionsPage.donate.algorithmWatchDesc'),
    },
    {
      name: 'Association Tournesol',
      href: 'https://tournesol.app/about/donate',
      desc: t('actionsPage.donate.associationTournesolDesc'),
    },
    {
      name: 'Mozilla Foundation',
      href: 'https://foundation.mozilla.org/fr/?form=donate-header',
      desc: t('actionsPage.donate.mozillaFoundationDesc'),
    },
    {
      name: 'Wikimedia Foundation',
      href: 'https://donate.wikimedia.org/wiki/Ways_to_Give',
      desc: t('actionsPage.donate.wikimediaFoundationDesc'),
    },
    {
      name: t('actionsPage.donate.yourLocalWikimediaChapter'),
      href: 'https://meta.wikimedia.org/wiki/Wikimedia_chapters',
      desc: t('actionsPage.donate.localWikimediaChaptersDesc'),
    },
  ];

  return (
    <Box sx={{ '& li': { mt: 1 } }}>
      <Typography variant="h4" fontStyle="italic" gutterBottom id="donate">
        {t(
          'actionsPage.donate.donateToOrganisationsFightingForQualityOfInformation'
        )}
      </Typography>
      <Box my={2}>
        <Alert severity="info" icon={false}>
          {t('actionsPage.donate.hereIsAlist')}
        </Alert>
      </Box>
      <OrganisationToDonateTo organizations={organizations} />
    </Box>
  );
};

export default Donate;
