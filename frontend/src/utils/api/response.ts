import { ProviderContext, VariantType } from 'notistack';
import { ApiError } from 'src/services/openapi';
import {
  contactAdministrator,
  showErrorAlert,
  showInfoAlert,
} from 'src/utils/notifications';

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
 *          displayErrors(enqueueSnackbar, reason);
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
 *          displayErrors(
 *            enqueueSnackbar,
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
export const displayErrors = (
  display: ProviderContext['enqueueSnackbar'],
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
        display(status.msg, { variant: status.variant });
        return;
      }
    }

    // HTTP 429 Too Many Requests are considered information
    if (reason.status === 429) {
      showInfoAlert(display, reason.body['detail']);
    } else {
      const newErrorMessages = Object.values(reason['body']).flat();
      // eslint-disable-next-line @typescript-eslint/ban-ts-comment
      // @ts-ignore
      newErrorMessages.map((msg) => showErrorAlert(display, msg));
    }
  } else {
    contactAdministrator(display, 'error', message);
  }
};
