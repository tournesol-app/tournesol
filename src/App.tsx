import React from 'react';
import { Switch, Route } from 'react-router-dom';

import HomePage from './pages/home/Home';
import LoginPage from './pages/login/Login';
import ComparisonsPage from './pages/comparisons/Comparisons';
import DonatePage from './pages/donate/Donate';
import { PrivateRoute } from './features/login/PrivateRoute';

function App() {
  return (
    <div className="App">
      <Switch>
        <Route path="/login">
          <LoginPage />
        </Route>
        <PrivateRoute path="/comparisons">
          <ComparisonsPage />
        </PrivateRoute>
        <Route path="/donate">
          <DonatePage />
        </Route>
        <Route path="/signup">
          <p>TODO: sign-up page</p>
        </Route>
        <Route path="/">
          <HomePage />
        </Route>
      </Switch>
    </div>
  );
}

export default App;
