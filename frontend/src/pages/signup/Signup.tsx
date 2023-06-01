import React, { useState } from 'react';
import { useTranslation, Trans } from 'react-i18next';
import { Grid, Button, Typography, Checkbox } from '@mui/material';
import {
  ContentHeader,
  ContentBox,
  Lines,
  FormTextField,
} from 'src/components';
import { useNotifications } from 'src/hooks';
import {
  AccountsService,
  ApiError,
  RegisterUserRequest,
} from 'src/services/openapi';
import { Link } from 'react-router-dom';

import { TRACKED_EVENTS, trackEvent } from 'src/utils/analytics';

const SignupSuccess = ({ email }: { email: string }) => {
  const { t } = useTranslation();
  return (
    <Typography>
      <Trans t={t} i18nKey="signup.successMessage">
        Success!
        <br />A verification link has been sent to <code>{{ email }}</code> .
      </Trans>
    </Typography>
  );
};

const Signup = () => {
  const { t } = useTranslation();

  const [apiError, setApiError] = useState<ApiError | null>(null);
  const [successEmailAddress, setSuccessEmailAddress] = useState<string | null>(
    null
  );
  const [acceptPolicy, setAcceptPolicy] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const { displayErrorsFrom } = useNotifications();

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setApiError(null);
    setIsLoading(true);
    const formData = new FormData(event.currentTarget);
    const formObject: unknown = Object.fromEntries(formData);
    try {
      const createdUser = await AccountsService.accountsRegisterCreate({
        requestBody: formObject as RegisterUserRequest,
      });
      setSuccessEmailAddress(createdUser.email || '');
      trackEvent(TRACKED_EVENTS.signup, { props: { state: 'created' } });
    } catch (err) {
      setApiError(err as ApiError);
      if (err?.status !== 400) {
        displayErrorsFrom(err);
      }
    }
    setIsLoading(false);
  };

  const formError = apiError?.status === 400 ? apiError.body : null;

  return (
    <>
      <ContentHeader title={t('signup.title')} />
      <ContentBox maxWidth="sm">
        {successEmailAddress !== null ? (
          <SignupSuccess email={successEmailAddress} />
        ) : (
          <form onSubmit={handleSubmit}>
            <Grid container spacing={3} direction="column" alignItems="stretch">
              {formError && (
                <Grid item xs={12}>
                  <Typography color="error">
                    {t('signup.accountCreationFailed')}
                    <br />
                    {formError?.non_field_errors && (
                      <Lines messages={formError.non_field_errors} />
                    )}
                  </Typography>
                </Grid>
              )}
              <Grid item xs={12}>
                <FormTextField
                  name="email"
                  label={t('emailAddress')}
                  autoComplete="email"
                  formError={formError}
                />
              </Grid>
              <Grid item xs={12}>
                <FormTextField
                  name="username"
                  label={t('username')}
                  formError={formError}
                  helperText={t(
                    'settings.captionUsernameWillAppearInPublicDatabase'
                  )}
                />
              </Grid>
              <Grid item xs={12}>
                <FormTextField
                  name="password"
                  label={t('password')}
                  type="password"
                  autoComplete="new-password"
                  formError={formError}
                />
              </Grid>
              <Grid item xs={12}>
                <FormTextField
                  name="password_confirm"
                  label={t('confirmYourPassword')}
                  type="password"
                  autoComplete="new-password"
                  formError={formError}
                />
              </Grid>
              <Grid item xs={12} display="flex" alignItems="center" gap={1}>
                <Checkbox
                  color="secondary"
                  checked={acceptPolicy}
                  onClick={() => setAcceptPolicy(!acceptPolicy)}
                />
                <span>
                  <Typography>
                    <Trans t={t} i18nKey="signup.iAgreeWithTheTerms">
                      I&apos;m at least 15 years old. I have read and I agree
                      with the{' '}
                      <Link to="/about/terms-of-service" target="_blank">
                        Terms of Service
                      </Link>{' '}
                      and the{' '}
                      <Link to="/about/privacy_policy" target="_blank">
                        Privacy Policy
                      </Link>
                      .
                    </Trans>
                  </Typography>
                </span>
              </Grid>
              <Grid item xs={12}>
                <Button
                  type="submit"
                  color="secondary"
                  fullWidth
                  disabled={!acceptPolicy || isLoading}
                  variant="contained"
                >
                  {t('signUpButton')}
                </Button>
              </Grid>
            </Grid>
          </form>
        )}
      </ContentBox>
    </>
  );
};

export default Signup;
