import React, { useState } from 'react';

import Button from '@material-ui/core/Button';
import Grid from '@material-ui/core/Grid';
import LinearProgress from '@material-ui/core/LinearProgress';
import Typography from '@material-ui/core/Typography';
import { useSnackbar } from 'notistack';

import { showErrorAlert } from '../../../utils/notifications';

import type { ApiRequestOptions } from 'src/services/openapi/core/ApiRequestOptions';
import { OpenAPI } from 'src/services/openapi';

// The method below replaces the auto-generated usersMeExportsAllRetrieve
// from services/openapi/core/request.ts because it does
// not support returning response.blob which we need for
// downloading files from the API endpoint /users/me/exports/all
async function usersMeExportsAllRetrieveBlob(): Promise<Blob> {
  const api_url = OpenAPI.BASE;
  const options: ApiRequestOptions = {
    method: 'GET',
    path: '/users/me/exports/all/',
  };
  const access_token =
    typeof OpenAPI.TOKEN === 'function'
      ? await OpenAPI.TOKEN(options)
      : OpenAPI.TOKEN;
  const headers = { Authorization: `Bearer ${access_token}` };
  const response = await fetch(`${api_url}${options.path}`, {
    credentials: 'include',
    method: options.method,
    headers: headers,
  });
  return response.blob();
}

const ExportAllDataForm = () => {
  const [loading, setLoading] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState('');
  const { enqueueSnackbar } = useSnackbar();

  const downloadExport = async () => {
    const zipFileBlob = await usersMeExportsAllRetrieveBlob();
    setDownloadUrl(window.URL.createObjectURL(zipFileBlob));
    setLoading(false);
  };

  const prepareExport = async () => {
    setLoading(true);
    setDownloadUrl('');
    try {
      await downloadExport();
    } catch (error) {
      showErrorAlert(
        enqueueSnackbar,
        'An error seems to have occurred. If this error persists, please contact us.'
      );
      setLoading(false);
    }
  };

  return (
    <Grid container spacing={2} direction="column" alignItems="stretch">
      <Grid item md={6}>
        <Typography>
          Download all the comparisons that you have submitted to Tournesol
        </Typography>
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
            Download file
          </Button>
        ) : (
          <Button
            type="button"
            fullWidth
            color="secondary"
            variant="contained"
            onClick={prepareExport}
          >
            Prepare export
          </Button>
        )}
      </Grid>
    </Grid>
  );
};

export default ExportAllDataForm;
