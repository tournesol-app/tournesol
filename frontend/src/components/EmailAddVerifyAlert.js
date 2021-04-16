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
          Your verified email address does not belong to a trusted institution. As a result,
          your
          ratings will not impact the Tournesol scores, and your comments will not be visible.
          Please register an email address
          to a trusted institution to impact Tournesol scores

          <EmailAddVerify />
        </Alert>)}
      {!isCertified && !domainRejected && (
        <Alert severity="info" className={`${classes.alertTop} class_pending`}>
          We are currently assessing the trustworthiness of the institution associated to your
          email address. Note that, as a result, your ratings may not impact the Tournesol
          scores, and your comments will not be visible.

          <EmailAddVerify />
        </Alert>)}
    </>
  );
};
