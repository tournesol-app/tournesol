import React from 'react';

import { useHistory, useParams } from 'react-router-dom';
import Button from '@material-ui/core/Button';

export default (props) => {
  const { verified, reset } = props;
  const { email } = useParams();
  const history = useHistory();
  return (
    <div id="id_email_instructions">
      {reset === 1 && (
        <p>
          If such username exists, we sent an e-mail to your
          address with a link to reset your passsword.
          Please check your inbox and spam folders.
        </p>
      )}
      {!reset && verified === 1 && (
      <p>Your e-mail address <b>{email}</b> was verified!</p>
      )}
      {!reset && !verified && (
      <p>A verification e-mail was sent to your address <b>{email}</b>.
        Please check your inbox and follow the link in the e-mail to verify it.
        Note that the certification email might have ended up in your spam mailbox
      </p>
      )}
      <Button
        onClick={() => history.push('/')}
        id={verified ?
          'button_home_page_verified_id' : 'button_home_page_to_verify_id'}
      >
        Home page
      </Button>
    </div>);
};
