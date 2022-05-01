import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import Button from '@mui/material/Button';
import Grid from '@mui/material/Grid';
import LinearProgress from '@mui/material/LinearProgress';
import Typography from '@mui/material/Typography';

import type { ApiRequestOptions } from 'src/services/openapi/core/ApiRequestOptions';
import { OpenAPI } from 'src/services/openapi';
import { useNotifications } from 'src/hooks';

// The method below replaces the auto-generated usersMeExportsAllRetrieve
// from services/openapi/core/request.ts because it does
// not support returning response.blob which we need for
// downloading files from the API endpoint /users/me/exports/all
async function usersMeExportsAllRetrieveBlob(): Promise<Response> {
  const api_url = OpenAPI.BASE;
  const options: ApiRequestOptions = {
    method: 'GET',
    url: '/users/me/exports/all/',
  };
  const access_token =
    typeof OpenAPI.TOKEN === 'function'
      ? await OpenAPI.TOKEN(options)
      : OpenAPI.TOKEN;
  const headers = { Authorization: `Bearer ${access_token}` };
  const response = await fetch(`${api_url}${options.url}`, {
    credentials: 'include',
    method: options.method,
    headers: headers,
  });
  return response;
}

const ExportAllDataForm = () => {
  const { t } = useTranslation();
  const { contactAdministrator, showErrorAlert, showTooManyRequests } =
    useNotifications();

  const [loading, setLoading] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState('');

  const downloadExport = async () => {
    const response = await usersMeExportsAllRetrieveBlob();

    if (response.ok === true) {
      const zipFileBlob = await response.blob();
      setDownloadUrl(window.URL.createObjectURL(zipFileBlob));
    } else {
      // avoid promises fulfilled by HTTP errors to be considered as successful
      if (response.status == 429) {
        showTooManyRequests();
      } else {
        showErrorAlert(response.statusText);
      }
    }

    setLoading(false);
  };

  const prepareExport = async () => {
    setLoading(true);
    setDownloadUrl('');
    try {
      await downloadExport();
    } catch (error) {
      contactAdministrator('error');
      setLoading(false);
    }
  };

  return (
    <Grid container spacing={2} direction="column" alignItems="stretch">
      <Grid item md={6}>
        <Typography>{t('settings.downloadAllComparisons')}</Typography>
      </Grid>
      <Grid item md={6}>
        {loading ? (
          <LinearProgress color="secondary" />
        ) : downloadUrl ? (
          <Button
            component="a"
            fullWidth
            href={downloadUrl}
            download="export-tournesol-data.zip"
            color="secondary"
            variant="outlined"
          >
            {t('settings.downloadFile')}
          </Button>
        ) : (
          <Button
            type="button"
            fullWidth
            color="secondary"
            variant="contained"
            onClick={prepareExport}
          >
            {t('settings.prepareExport')}
          </Button>
        )}
      </Grid>
    </Grid>
  );
};

export default ExportAllDataForm;
