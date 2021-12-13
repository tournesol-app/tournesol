import React, { useState } from 'react';
import { Grid, Button, Typography, Checkbox } from '@material-ui/core';
import {
  Alert,
  ContentHeader,
  ContentBox,
  Lines,
  FormTextField,
} from 'src/components';
import { AccountsService, RegisterUser, ApiError } from 'src/services/openapi';
import { Link } from 'react-router-dom';

const SignupSuccess = ({ email }: { email: string }) => (
  <Typography>
    Success!
    <br />A verification link has been sent to <code>{email}</code> .
  </Typography>
);

const Signup = () => {
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
      <ContentHeader title="Account creation" />
      <ContentBox maxWidth="xs">
        {successEmailAddress !== null ? (
          <SignupSuccess email={successEmailAddress} />
        ) : (
          <form onSubmit={handleSubmit}>
            <Grid container spacing={3} direction="column" alignItems="stretch">
              {formError && (
                <Grid item xs={12}>
                  <Typography color="error">
                    Account creation failed.
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
                  label="Email address"
                  formError={formError}
                />
              </Grid>
              <Grid item xs={12}>
                <FormTextField
                  name="username"
                  label="Username"
                  formError={formError}
                />
              </Grid>
              <Grid item xs={12}>
                <FormTextField
                  name="password"
                  label="Password"
                  type="password"
                  formError={formError}
                />
              </Grid>
              <Grid item xs={12}>
                <FormTextField
                  name="password_confirm"
                  label="Confirm your password"
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
                  I have read and agree with the{' '}
                  <Link to="/about/privacy_policy" target="_blank">
                    privacy policy
                  </Link>
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
                  Sign up
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
