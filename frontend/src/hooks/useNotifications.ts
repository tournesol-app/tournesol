import { useCallback } from 'react';
import { useSnackbar, VariantType } from 'notistack';
import { useTranslation } from 'react-i18next';
import { ApiError } from 'src/services/openapi';

/**
 * Provide several functions allowing to display different kinds of message to
 * the user, without interrupting its experience.
 */
export const useNotifications = () => {
  const { enqueueSnackbar } = useSnackbar();
  const { t } = useTranslation();

  /**
   * Display an alert variant of any type, followed by an invitation to retry
   * later, or reach an administrator.
   */
  const contactAdministrator = useCallback(
    (variant: VariantType, message?: string) => {
      if (!message) {
        message = t('notifications.errorOccurred');
      }
      enqueueSnackbar(t('notifications.tryAgainLaterOrContactAdministrator'), {
        variant: 'warning',
      });
      enqueueSnackbar(message, { variant: variant });
    },
    [enqueueSnackbar, t]
  );

  /**
   * Display an info alert, followed by an invitation to report an issue.
   *
   * Contrary to `contactAdministrator` this function use only the info alert
   * variant to notify the user of the presence of non-impacting error. It should
   * not be used to report blocking errors or errors requiring an action from the
   * user.
   */
  const contactAdministratorLowSeverity = useCallback(
    (message?: string) => {
      if (!message) {
        message = t('notifications.nonImpactingError');
      }
      enqueueSnackbar(
        t('notifications.pleaseContactAnAdministratorToReportIssue'),
        {
          variant: 'info',
        }
      );
      enqueueSnackbar(message, { variant: 'info' });
    },
    [enqueueSnackbar, t]
  );

  const showSuccessAlert = useCallback(
    (message: React.ReactNode) => {
      enqueueSnackbar(message, {
        variant: 'success',
      });
    },
    [enqueueSnackbar]
  );

  const showErrorAlert = useCallback(
    (message: React.ReactNode) => {
      enqueueSnackbar(message, {
        variant: 'error',
      });
    },
    [enqueueSnackbar]
  );

  const showInfoAlert = useCallback(
    (message: React.ReactNode) => {
      enqueueSnackbar(message, {
        variant: 'info',
      });
    },
    [enqueueSnackbar]
  );

  const showTooManyRequests = useCallback(
    (message?: string) => {
      if (!message) {
        message = t('notifications.youTemporarilyMadeTooManyRequests.');
      }
      enqueueSnackbar(message, { variant: 'info' });
    },
    [enqueueSnackbar, t]
  );

  const displayMessagesFromReasonBody = useCallback(
    (reasonBody) => {
      if (typeof reasonBody === 'string') {
        showErrorAlert(reasonBody);
      } else if (
        Object.prototype.toString.call(reasonBody) === '[object Object]'
      ) {
        Object.values(reasonBody).map((value) =>
          displayMessagesFromReasonBody(value)
        );
      } else if (Array.isArray(reasonBody)) {
        reasonBody.map((value) => displayMessagesFromReasonBody(value));
      }
    },
    [showErrorAlert]
  );

  /**
   * Display all errors contained in an `ApiError` object.
   *
   * This function provides a generic way to display all error messages returned
   * by an API call. It can be used in every form to harmonize the messages
   * processing.
   *
   * Ex
   *      const response = await addNewVideo({ video_id }).catch(
   *        (reason: ApiError) => {
   *          displayErrorsFrom(reason);
   *        }
   *      );
   *
   * The optional `overrideStatuses` parameter allows the developers to display
   * in the UI custom messages for a specific set of HTTP response status code.
   * They will override those contained in the response.
   *
   * Ex
   *      const response = await addNewVideo({ video_id }).catch(
   *        (reason: ApiError) => {
   *          displayErrorsFrom(
   *            reason,
   *            'Sorry, an error has occurred. The video cannot be added.',
   *            [{ status: 409, variant: 'error', msg: 'Video already added.' }]
   *          );
   *        }
   *      );
   *
   * Unknown `Error` or malformed `ApiError` are displayed as an invitation to
   * try again later or contact an administrator.
   */
  const displayErrorsFrom = useCallback(
    (
      reason: ApiError | Error,
      message?: string,
      overrideStatuses?: Array<{
        status: number;
        msg: string;
        variant: VariantType;
      }>
    ) => {
      if (reason && 'body' in reason) {
        // override message from the API
        if (overrideStatuses) {
          const status = overrideStatuses.find(
            (elem) => elem.status === reason.status
          );
          if (status) {
            enqueueSnackbar(status.msg, { variant: status.variant });
            return;
          }
        }

        // HTTP 429 Too Many Requests are considered information
        if (reason.status === 429) {
          showInfoAlert(reason.body['detail']);
        } else {
          const body = reason.body;

          displayMessagesFromReasonBody(body);
        }
      } else {
        contactAdministrator('error', message);
      }
    },
    [
      enqueueSnackbar,
      contactAdministrator,
      showInfoAlert,
      displayMessagesFromReasonBody,
    ]
  );

  return {
    showInfoAlert,
    showSuccessAlert,
    showErrorAlert,
    showTooManyRequests,
    contactAdministrator,
    contactAdministratorLowSeverity,
    displayErrorsFrom,
  };
};
