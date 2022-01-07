import React, { useState } from 'react';
import { useTranslation, Trans } from 'react-i18next';
import { Grid, Button, Typography, Checkbox } from '@mui/material';
import {
  Alert,
  ContentHeader,
  ContentBox,
  Lines,
  FormTextField,
} from 'src/components';
import { AccountsService, RegisterUser, ApiError } from 'src/services/openapi';
import { Link } from 'react-router-dom';

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

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setApiError(null);
    setIsLoading(true);
    const formData = new FormData(event.currentTarget);
    const formObject: unknown = Object.fromEntries(formData);
    try {
      const createdUser = await AccountsService.accountsRegisterCreate({
        requestBody: formObject as RegisterUser,
      });
      setSuccessEmailAddress(createdUser.email || '');
    } catch (err) {
      setApiError(err as ApiError);
    }
    setIsLoading(false);
  };

  const formError = apiError?.status === 400 ? apiError.body : null;
  const genericError =
    apiError?.status !== 400 ? apiError?.message || '' : null;

  return (
    <>
      <ContentHeader title={t('signup.title')} />
      <ContentBox maxWidth="xs">
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
                  formError={formError}
                />
              </Grid>
              <Grid item xs={12}>
                <FormTextField
                  name="username"
                  label={t('username')}
                  formError={formError}
                />
              </Grid>
              <Grid item xs={12}>
                <FormTextField
                  name="password"
                  label={t('password')}
                  type="password"
                  formError={formError}
                />
              </Grid>
              <Grid item xs={12}>
                <FormTextField
                  name="password_confirm"
                  label={t('confirmYourPassword')}
                  type="password"
                  formError={formError}
                />
              </Grid>
              <Grid item xs={12}>
                <Checkbox
                  checked={acceptPolicy}
                  onClick={() => setAcceptPolicy(!acceptPolicy)}
                />
                <span>
                  <Trans t={t} i18nKey="signup.iAgreeWithThePrivacyPolicy">
                    I have read and agree with the{' '}
                    <Link to="/about/privacy_policy" target="_blank">
                      privacy policy
                    </Link>
                  </Trans>
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
            {genericError && <Alert>❌ {genericError}</Alert>}
          </form>
        )}
      </ContentBox>
    </>
  );
};

export default Signup;
