import React from 'react';
import { ProviderContext, VariantType } from 'notistack';

/**
 * Display an alert variant of any type, followed by an invitation to retry
 * later, or reach an administrator.
 */
export const contactAdministrator = (
  display: ProviderContext['enqueueSnackbar'],
  variant: VariantType,
  message?: string
) => {
  if (!message) {
    message = 'Sorry an error has occurred.';
  }
  display(
    'Please, try again later, or contact an administrator if the issue persists.',
    {
      variant: 'warning',
    }
  );
  display(message, { variant: variant });
};

/**
 * Display an info alert, followed by an invitation to report an issue.
 *
 * Contrary to `contactAdministrator` this function use only the info alert
 * variant to notify the user of the presence of non-impacting error. It should
 * not be used to report blocking errors or errors requiring an action from the
 * user.
 */
export const contactAdministratorLowSeverity = (
  display: ProviderContext['enqueueSnackbar'],
  message?: string
) => {
  if (!message) {
    message = 'Oops, a non impacting error occurred.';
  }
  display('Please, contact an administrator to report the issue.', {
    variant: 'info',
  });
  display(message, { variant: 'info' });
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

export const showInfoAlert = (
  enqueueSnackbar: ProviderContext['enqueueSnackbar'],
  message: React.ReactNode
) => {
  enqueueSnackbar(message, {
    variant: 'info',
  });
};
