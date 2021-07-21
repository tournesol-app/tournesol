import React from 'react';
import './App.css';
import Login from './features/login/Login';
import Frame from './features/frame/Frame';

function App() {
  return (
    <div className="App">
      <Frame />
      <Login />
    </div>
  );
}

export default App;
