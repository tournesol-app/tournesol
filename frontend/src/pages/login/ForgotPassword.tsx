import React, { useState } from 'react';
import { useTranslation, Trans } from 'react-i18next';

import { Grid, Button, Typography, Box } from '@mui/material';

import {
  ContentHeader,
  ContentBox,
  Lines,
  FormTextField,
  InternalLink,
} from 'src/components';
import { useNotifications } from 'src/hooks';
import {
  AccountsService,
  ApiError,
  DefaultSendResetPasswordLink,
} from 'src/services/openapi';

const ResetSuccess = () => {
  const { t } = useTranslation();
  return (
    <Typography>
      <Trans t={t} i18nKey="reset.ifUserExistsResetLinkWillBeSent">
        Done!
        <br />
        If this user exists, an email will be sent with a reset link.
      </Trans>
    </Typography>
  );
};

const ForgotPassword = () => {
  const { t } = useTranslation();
  const { displayErrorsFrom } = useNotifications();
  const [apiError, setApiError] = useState<ApiError | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsLoading(true);
    const formData = new FormData(event.currentTarget);
    const formObject: unknown = Object.fromEntries(formData);
    try {
      await AccountsService.accountsSendResetPasswordLinkCreate({
        requestBody: formObject as DefaultSendResetPasswordLink,
      });
      setSuccess(true);
    } catch (err) {
      setApiError(err as ApiError);
      if (err?.status !== 400) {
        displayErrorsFrom(err);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const formError = apiError?.status === 400 ? apiError.body : null;

  return (
    <>
      <ContentHeader title={t('reset.resetYourPassword')} />
      <ContentBox maxWidth={success ? 'sm' : 'xs'}>
        {success ? (
          <ResetSuccess />
        ) : (
          <>
            <form onSubmit={handleSubmit}>
              <Grid
                container
                spacing={3}
                direction="column"
                alignItems="stretch"
              >
                {formError && (
                  <Grid item xs={12}>
                    <Typography color="error">
                      {t('reset.failToSendResetLink')}
                      <br />
                      {formError?.non_field_errors && (
                        <Lines messages={formError.non_field_errors} />
                      )}
                    </Typography>
                  </Grid>
                )}
                <Grid item xs={12}>
                  <FormTextField
                    name="login"
                    label={t('usernameOrEmail')}
                    formError={formError}
                  />
                </Grid>
                <Grid item xs={12}>
                  <Button
                    type="submit"
                    color="secondary"
                    fullWidth
                    variant="contained"
                    disabled={isLoading}
                  >
                    {t('reset.sendResetEmailButton')}
                  </Button>
                </Grid>
              </Grid>
            </form>
            <Box my={2}>
              <InternalLink to="/login">{t('reset.backToLogIn')}</InternalLink>
            </Box>
          </>
        )}
      </ContentBox>
    </>
  );
};

export default ForgotPassword;
