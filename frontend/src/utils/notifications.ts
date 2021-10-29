import React from 'react';
import { ProviderContext, VariantType } from 'notistack';

/**
 * Display an alert variant, followed by an invitation to reach an
 * administrator.
 */
export const contactAdministrator = (
  display: ProviderContext['enqueueSnackbar'],
  variant: VariantType,
  message?: string
) => {
  if (!message) {
    message = 'Sorry an error has occurred.';
  }
  display('Please, contact an administrator to report the issue.', {
    variant: 'warning',
  });
  display(message, { variant: variant });
};

export const showSuccessAlert = (
  enqueueSnackbar: ProviderContext['enqueueSnackbar'],
  message: React.ReactNode
) => {
  enqueueSnackbar(message, {
    variant: 'success',
  });
};

export const showErrorAlert = (
  enqueueSnackbar: ProviderContext['enqueueSnackbar'],
  message: React.ReactNode
) => {
  enqueueSnackbar(message, {
    variant: 'error',
  });
};
