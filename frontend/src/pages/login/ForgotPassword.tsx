import React, { useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { Grid, Button, Typography, Box, Link } from '@mui/material';
import {
  ContentHeader,
  ContentBox,
  Lines,
  FormTextField,
} from 'src/components';
import {
  AccountsService,
  ApiError,
  DefaultSendResetPasswordLink,
} from 'src/services/openapi';
import { useNotifications } from 'src/hooks';

const ResetSuccess = () => (
  <Typography>
    Done!
    <br />
    If this user exists, an email will be sent with a reset link.
  </Typography>
);

const ForgotPassword = () => {
  const { showErrorAlert } = useNotifications();
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
        showErrorAlert(err?.message || 'Server error');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const formError = apiError?.status === 400 ? apiError.body : null;

  return (
    <>
      <ContentHeader title="Reset your password" />
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
                      Failed to send the reset link.
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
                    label="Username"
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
                    Send reset email
                  </Button>
                </Grid>
              </Grid>
            </form>
            <Box my={2}>
              <Link
                component={RouterLink}
                to="/login"
                color="secondary"
                underline="hover"
              >
                Back to Log in
              </Link>
            </Box>
          </>
        )}
      </ContentBox>
    </>
  );
};

export default ForgotPassword;
