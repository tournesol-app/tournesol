import React from 'react';
import './App.css';
import HomePage from './pages/home/Home';
import LoginPage from './pages/login/Login';
import ComparisonsPage from './pages/comparisons/Comparisons';
import {
  BrowserRouter as Router,
  Switch,
  Route,
} from "react-router-dom";

function App() {
  return (
    <Router>
      <div className="App">
        <Switch>
          <Route path="/login">
            <LoginPage />
          </Route>
          <Route path="/comparisons">
            <ComparisonsPage />
          </Route>
          <Route path="/">
            <HomePage />
          </Route>
        </Switch>
      </div>
    </Router>
  );
}

export default App;
