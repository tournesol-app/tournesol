import React from 'react';

import { Switch, Route } from 'react-router-dom';

import Home from './Home';
import UserInterface from './UserInterface';
import ExpertInterface from './ExpertInterface';
import VideoList from './VideoList';
import VideoDetails from './VideoDetails';
import VideoRatings from './VideoRatings';
import Inconsistencies from './Inconsistencies';
import Representative from './RepresentativeCheckInterface';
import PersonalInfo from './PersonalInfo';
import UserPage from './UserPage';
import EmailInstructions from './EmailInstructions';
import EmailDomains from './EmailDomains';
import PrivacyPolicy from './PrivacyPolicy';
import Signup from './Signup';
import Login from './Login';
import Logout from './Logout';
import ChangeUsername from './ChangeUsername';
import ResetPassword from './ResetPassword';
import SetPassword from './SetPassword';
import CommentMentionPage from './CommentMentionPage';
import RateLater from './RateLater';
import OnlineUpdateDemo from './OnlineUpdateDemo';

export default () => (
  <Switch>
    <Route path="/info/">
      <PersonalInfo />
    </Route>
    <Route path="/recommendations/:defaultSearchModel">
      <UserInterface />
    </Route>
    <Route path="/recommendations">
      <UserInterface />
    </Route>
    <Route path="/user/:userId">
      <UserPage />
    </Route>
    <Route path="/rate/:videoIdA/:videoIdB">
      <ExpertInterface />
    </Route>
    <Route path="/rate/">
      <ExpertInterface />
    </Route>
    <Route path="/ratings/:videoId">
      <VideoRatings />
    </Route>
    <Route path="/ratings/">
      <VideoRatings />
    </Route>
    <Route path="/representative/">
      <Representative />
    </Route>
    <Route path="/videos/">
      <VideoList />
    </Route>
    <Route path="/details/:videoId">
      <VideoDetails />
    </Route>
    <Route path="/details">
      <VideoDetails />
    </Route>
    <Route path="/inconsistencies">
      <Inconsistencies />
    </Route>
    <Route path="/email_domains">
      <EmailDomains />
    </Route>
    <Route path="/email_show_instructions/:email">
      <EmailInstructions verified={0} />
    </Route>
    <Route path="/email_verified/:email">
      <EmailInstructions verified={1} />
    </Route>
    <Route path="/privacy_policy">
      <PrivacyPolicy />
    </Route>
    <Route path="/signup">
      <Signup />
    </Route>
    <Route path="/login">
      <Login />
    </Route>
    <Route path="/logout">
      <Logout />
    </Route>
    <Route path="/change_username">
      <ChangeUsername />
    </Route>
    <Route path="/reset_password">
      <ResetPassword />
    </Route>
    <Route path="/email_show_instructions_reset">
      <EmailInstructions reset={1} />
    </Route>
    <Route path="/set_password">
      <SetPassword />
    </Route>
    <Route path="/comment_mentions">
      <CommentMentionPage />
    </Route>
    <Route path="/rate_later">
      <RateLater />
    </Route>
    <Route path="/rate_later_add/:videoIdAdd">
      <RateLater />
    </Route>
    <Route path="/online/:videoIdA/:videoIdB">
      <OnlineUpdateDemo />
    </Route>
    <Route path="/">
      <Home />
    </Route>
  </Switch>
);
