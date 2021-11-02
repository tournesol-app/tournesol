import React from 'react';

import { Box, Divider, Grid, Typography } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';

import ContentHeader from '../../../components/ContentHeader';
import PasswordForm from '../../../features/settings/account/PasswordForm';
import DeleteAccountForm from '../../../features/settings/account/DeleteAccountForm';
import SettingsMenu from '../../../features/settings/SettingsMenu';
import { EmailAddressForm } from 'src/features/settings/account/EmailAddressForm';

const useStyles = makeStyles((theme) => ({
  titleDanger: { color: theme.palette.error.main },
}));

const Section = ({
  title,
  children,
  ...rest
}: {
  title: string | React.ReactNode;
  children: React.ReactNode;
  [rest: string]: unknown;
}) => {
  let sectionTitle;
  if (typeof title === 'string') {
    sectionTitle = (
      <Typography variant="h4" color="secondary">
        {title}
      </Typography>
    );
  } else {
    sectionTitle = title;
  }

  return (
    <Grid item container style={{ paddingBottom: '40px' }}>
      <Grid item xs={12}>
        <Box marginBottom={2}>
          {sectionTitle}
          <Divider />
        </Box>
      </Grid>
      <Grid item {...rest}>
        {children}
      </Grid>
    </Grid>
  );
};

export const AccountPage = () => {
  const classes = useStyles();
  return (
    <>
      <ContentHeader title="Settings > Account" />
      <Box m={4}>
        <Grid container spacing={4}>
          <Grid item xs={12} sm={12} md={3}>
            <SettingsMenu />
          </Grid>
          <Grid
            container
            item
            direction="column"
            alignItems="stretch"
            xs={12}
            sm={12}
            md={9}
            spacing={3}
          >
            <Section title="Change email address" xs={12}>
              <EmailAddressForm />
            </Section>
            <Section title="Change password" xs={12} md={6}>
              <PasswordForm />
            </Section>
            <Box marginTop={8} />
            <Section
              title={
                <Typography variant="h4" className={classes.titleDanger}>
                  Delete account
                </Typography>
              }
              md={6}
            >
              <DeleteAccountForm />
            </Section>
          </Grid>
        </Grid>
      </Box>
    </>
  );
};

export default AccountPage;
