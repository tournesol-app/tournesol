import React from 'react';
import './App.css';
import HomePage from './pages/home/Home';
import LoginPage from './pages/login/Login';
import ComparisonsPage from './pages/comparisons/Comparisons';
import { Switch, Route } from 'react-router-dom';
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
        <Route path="/">
          <HomePage />
        </Route>
      </Switch>
    </div>
  );
}

export default App;
