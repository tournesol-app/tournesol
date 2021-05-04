import React, { useState } from 'react';

import { makeStyles } from '@material-ui/core/styles';
import Alert from '@material-ui/lab/Alert';
import { TournesolAPI } from '../api';
import EmailAddVerify from './EmailAddVerify';

const useStyles = makeStyles(() => ({
  alertTop: {
    marginBottom: '15px',
    textAlign: 'center',
  },
}));

export default () => {
  const classes = useStyles();

  const [domainRejected, setDomainRejected] = useState(false);
  const [isCertified, setIsCertified] = useState(true);
  const [userInfoRequested, setUserInfoRequested] = useState(false);

  if (!userInfoRequested) {
    setUserInfoRequested(true);
    const api = new TournesolAPI.UserInformationApi();
    api.userInformationRetrieve(window.user_information_id, (err, res) => {
      if (!err) {
        setDomainRejected(res.is_domain_rejected);
        setIsCertified(res.is_certified);
      }
    });
  }
  return (
    <>
      {!isCertified && domainRejected && (
        <Alert severity="error" className={`${classes.alertTop} class_rejected`}>
          The email domain of your verified email address
          is currently not trusted by Tournesol.
          We fear that this email domain could be used by malicious
          entities to create numerous fake accounts
          and gain control of Tournesol through a{' '}
          <a href="https://wiki.tournesol.app/index.php/51%25_attack">51% attack</a>.
          As a result, your ratings will not impact the certified Tournesol scores,
          and your comments will not be visible.
          You can gain the capabilities of certified Tournesol accounts
          by registering another email address from a{' '}
          <a href="https://wiki.tournesol.app/index.php/Trusted_email_domains">trusted email domain</a>

          <EmailAddVerify />
        </Alert>)}
      {!isCertified && !domainRejected && (
        <Alert severity="info" className={`${classes.alertTop} class_pending`}>
          We are currently assessing the trustworthiness of the email domain associated to your
          email address.
          This manual operation may take a few days.
          This certification is critical for the safety of Tournesol,
          as it protects the collaborative platform against{' '}
          <a href="https://wiki.tournesol.app/index.php/51%25_attack">51% attacks</a>.
          You can gain the capabilities of certified Tournesol accounts
          by registering another email address from a{' '}
          <a href="https://wiki.tournesol.app/index.php/Trusted_email_domains">trusted email domain</a>

          <EmailAddVerify />
        </Alert>)}
    </>
  );
};
