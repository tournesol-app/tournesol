import React from 'react';
import { useTranslation, Trans } from 'react-i18next';
import { Typography, Button } from '@mui/material';

// PublicDownloadSection is a paragraph displayed on the HomePage
// that helps users know how to download the public video comparisons available for their use case
const PublicDownloadSection = () => {
  const { t } = useTranslation();
  const api_url = process.env.REACT_APP_API_URL;
  return (
    <>
      <Typography variant="h1">{t('about.publicDatabase')}</Typography>
      <Typography paragraph>
        <Trans t={t} i18nKey="about.publicDatabaseDetailAndLicense">
          Contributors on Tournesol can decide to make their data public. We
          hope this important data will prove useful for researchers on ethics
          of algorithms and large scale recommender systems. Our public database
          can be downloaded by clicking the button below and is published under{' '}
          <a
            href="https://opendatacommons.org/licenses/by/1-0/"
            style={{ color: 'white' }}
          >
            Open Data Commons Attribution License (ODC-By)
          </a>
          .
        </Trans>
      </Typography>
      <Typography paragraph>
        {t('about.publicDatabaseThanksToContributors')}
      </Typography>

      <Button
        component="a"
        href={`${api_url}/exports/comparisons/`}
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
