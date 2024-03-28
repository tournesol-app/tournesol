import React from 'react';
import { useTranslation, Trans } from 'react-i18next';

import { Typography, Button } from '@mui/material';

import { ExternalLink } from 'src/components';
import { getPollStats } from 'src/features/statistics/stats';
import { useCurrentPoll, useStats } from 'src/hooks';

// PublicDownloadSection is a paragraph displayed on the HomePage
// that helps users know how to download the public video comparisons available for their use case
const PublicDownloadSection = () => {
  const { t } = useTranslation();
  const { name: pollName } = useCurrentPoll();

  const api_url = import.meta.env.REACT_APP_API_URL;

  const stats = useStats({ poll: pollName });
  const pollStats = getPollStats(stats, pollName);

  const userCount = stats.active_users.total ?? 0;
  const comparisonCount = pollStats?.comparisons.total ?? 0;
  const comparedEntityCount = pollStats?.compared_entities.total ?? 0;

  return (
    <>
      <Typography variant="h1">{t('about.publicDatabase')}</Typography>
      <Typography paragraph>
        <Trans t={t} i18nKey="about.publicDatabaseDetailAndLicense">
          Contributors on Tournesol can decide to make their data public. We
          hope this important data will prove useful for researchers on ethics
          of algorithms and large scale recommender systems. Our public database
          can be downloaded by clicking the button below and is published under{' '}
          <ExternalLink
            href="https://opendatacommons.org/licenses/by/1-0/"
            sx={{ color: 'white' }}
          >
            Open Data Commons Attribution License (ODC-By)
          </ExternalLink>
          .
        </Trans>
      </Typography>
      <Typography paragraph>
        <Trans t={t} i18nKey="about.publicDatabaseThanksToContributors">
          Finally, we would like to thank all the contributors who compared
          videos on Tournesol. We count so far about {{ userCount }} users who
          compared {{ comparisonCount }} times more than{' '}
          {{ comparedEntityCount }} videos.
        </Trans>
      </Typography>

      <Button
        component="a"
        href={`${api_url}/exports/all/`}
        download="tournesol_public_export.csv"
        color="primary"
        variant="contained"
      >
        {t('clickToDownload')}
      </Button>
    </>
  );
};

export default PublicDownloadSection;
