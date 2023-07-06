import React, { useState } from 'react';
import { useTranslation, Trans } from 'react-i18next';
import { Link } from 'react-router-dom';

import {
  Grid,
  Button,
  Typography,
  Checkbox,
  Alert,
  AlertTitle,
  Divider,
  Box,
} from '@mui/material';
import EmailIcon from '@mui/icons-material/Email';

import {
  ContentHeader,
  ContentBox,
  Lines,
  FormTextField,
} from 'src/components';
import NotificationsEmailResearch from 'src/features/settings/preferences/fields/NotificationsEmailResearch';
import NotificationsEmailNewFeatures from 'src/features/settings/preferences/fields/NotificationsEmailNewFeatures';
import { useNotifications } from 'src/hooks';
import {
  AccountsService,
  ApiError,
  Notifications_langEnum,
} from 'src/services/openapi';
import { TRACKED_EVENTS, trackEvent } from 'src/utils/analytics';
import { resolvedLangToNotificationsLang } from 'src/utils/userSettings';

const SignupSuccess = ({ email }: { email: string }) => {
  const { t } = useTranslation();
  return (
    <Alert severity="success">
      <AlertTitle>{t('signup.welcome')}</AlertTitle>
      <Trans t={t} i18nKey="signup.successMessage">
        A verification link has been sent to <code>{{ email }}</code> .
      </Trans>
    </Alert>
  );
};

const Signup = () => {
  const { t, i18n } = useTranslation();
  const { displayErrorsFrom } = useNotifications();

  const [apiError, setApiError] = useState<ApiError | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const [successEmailAddress, setSuccessEmailAddress] = useState<string | null>(
    null
  );

  const [acceptPolicy, setAcceptPolicy] = useState(false);

  // Legally, the notification settings must be false by default.
  const [notififResearch, setNotififResearch] = useState(false);
  const [notifNewFeatures, setNnotifNewFeatures] = useState(false);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setApiError(null);
    setIsLoading(true);

    const formData = new FormData(event.currentTarget);

    try {
      const createdUser = await AccountsService.accountsRegisterCreate({
        requestBody: {
          email: (formData.get('email') as string) ?? '',
          username: (formData.get('username') as string) ?? '',
          password: (formData.get('password') as string) ?? '',
          password_confirm: (formData.get('password_confirm') as string) ?? '',
          settings: {
            general: {
              notifications__lang: resolvedLangToNotificationsLang(
                i18n.resolvedLanguage
              ) as Notifications_langEnum,
              notifications_email__research: notififResearch,
              notifications_email__new_features: notifNewFeatures,
            },
          },
        },
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
                  name="accept_terms"
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
                <Box py={2}>
                  <Divider>
                    <Box display="flex" alignItems="center">
                      <EmailIcon color="secondary" />
                    </Box>
                  </Divider>
                </Box>
              </Grid>
              <Grid item xs={12}>
                <NotificationsEmailResearch
                  value={notififResearch}
                  onChange={(value) => setNotififResearch(value)}
                />
              </Grid>
              <Grid item xs={12}>
                <NotificationsEmailNewFeatures
                  value={notifNewFeatures}
                  onChange={(value) => setNnotifNewFeatures(value)}
                />
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
