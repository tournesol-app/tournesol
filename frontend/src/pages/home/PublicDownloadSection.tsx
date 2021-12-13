import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Typography, Button, Box } from '@material-ui/core';
import { useSnackbar } from 'notistack';
import LinearProgress from '@material-ui/core/LinearProgress';
import { showErrorAlert } from '../../utils/notifications';

import type { ApiRequestOptions } from 'src/services/openapi/core/ApiRequestOptions';
import { OpenAPI } from 'src/services/openapi';

// PublicDownloadSection is a paragraph displayed on the HomePage
// that helps users know how to download the public video comparisons available for their use case
const PublicDownloadSection = () => {
    const [loading, setLoading] = useState(false);
    const [downloadUrl, setDownloadUrl] = useState('');
    const { enqueueSnackbar } = useSnackbar();

    async function ExportsPublicComparisonsAllRetrieveBlob(): Promise<Blob> {
        const api_url = OpenAPI.BASE;
        const options: ApiRequestOptions = {
          method: 'GET',
          path: '/exports/comparisons/',
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

    const downloadExport = async () => {
        const csvFileBlob = await ExportsPublicComparisonsAllRetrieveBlob();
        setDownloadUrl(window.URL.createObjectURL(csvFileBlob));
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
    <Box
      display="flex"
      flexDirection="column"
      color="white"
      maxWidth="640px"
      alignItems="flex-start"
    >
      <Typography variant="h1">Download Public Dataset!</Typography>
      <Typography paragraph>
      Contributors on Tournesol can decide to make their data public. 
      You may download the dataset of all data publicly available. 
      We hope this important data will prove useful for researchers on 
      ethics of algorithms and large scale recommender systems.
      </Typography> 
      {loading ? (
          <LinearProgress color="secondary" />
          ) : downloadUrl ? (
            <Button
              component="a"
              fullWidth
              href={downloadUrl}
              download="export.csv"
              color="secondary"
              variant="outlined"
            >
              Download file
            </Button>
          ) : (
            <Button
              color="primary"
              variant="contained"
              onClick={prepareExport}
            >
              Click to Download
            </Button>
      )}
    </Box>
  );
};

export default PublicDownloadSection;
