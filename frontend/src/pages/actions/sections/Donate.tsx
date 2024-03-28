import React from 'react';
import { useTranslation } from 'react-i18next';

import { Alert, Box, Typography } from '@mui/material';

import { ExternalLink } from 'src/components';

interface Organization {
  name: string;
  desc: string;
  href: string;
  hrefDonate?: string;
}

const OrganisationToDonateTo = ({
  organizations,
}: {
  organizations: Organization[];
}) => {
  const { t } = useTranslation();
  return (
    <Box display="flex" flexDirection="column" gap={4}>
      {organizations.map((organisation, idx) => (
        <Box key={`organization_${idx}`}>
          <Box display="flex" gap={1}>
            <Typography variant="h6" gutterBottom>
              {organisation.name}
            </Typography>
            {'·'}
            <ExternalLink href={organisation.href}>
              {t('actionsPage.donate.website')}
            </ExternalLink>
            {organisation.hrefDonate && (
              <>
                {'·'}
                <ExternalLink href={organisation.hrefDonate}>
                  {t('actionsPage.donate.donate')}
                </ExternalLink>
              </>
            )}
          </Box>
          <Typography>{organisation.desc}</Typography>
        </Box>
      ))}
    </Box>
  );
};

const Donate = () => {
  const { t } = useTranslation();

  const organizations = [
    {
      name: 'AlgorithmWatch',
      desc: t('actionsPage.donate.algorithmWatchDesc'),
      href: 'https://algorithmwatch.org/en/',
      hrefDonate: 'https://algorithmwatch.org/en/donate/',
    },
    {
      name: 'Association Tournesol',
      desc: t('actionsPage.donate.associationTournesolDesc'),
      href: 'https://tournesol.app',
      hrefDonate: 'https://tournesol.app/about/donate',
    },
    {
      name: 'Mozilla Foundation',
      desc: t('actionsPage.donate.mozillaFoundationDesc'),
      href: 'https://foundation.mozilla.org',
      hrefDonate: 'https://foundation.mozilla.org?form=donate-header',
    },
    {
      name: 'Wikimedia Foundation',
      desc: t('actionsPage.donate.wikimediaFoundationDesc'),
      href: 'https://www.wikimedia.org',
      hrefDonate: 'https://donate.wikimedia.org/wiki/Ways_to_Give',
    },
    {
      name: t('actionsPage.donate.yourLocalWikimediaChapter'),
      desc: t('actionsPage.donate.localWikimediaChaptersDesc'),
      href: 'https://meta.wikimedia.org/wiki/Wikimedia_chapters',
    },
  ];

  return (
    <Box>
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
