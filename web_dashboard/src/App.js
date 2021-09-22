import React, { useState, useEffect } from 'react'
import ScopePage from './components/ScopePage/ScopePage'
import ControlWidget from './components/ControlWidget/ControlWidget'
import Header from './components/Header'
import './App.css';
import HardwarePage from './components/HardwarePage/HardwarePage';

function App() {
    const [display, setDisplay] = useState("scope");
    var displayComponent;

    if (display == "scope") {
        displayComponent = <ScopePage />
    }
    else if (display == "hardware") {
        displayComponent = <HardwarePage />
    }

  return (
      <div className="App">
          <Header setDisplay={ setDisplay }/>
          <div className="appWindow">
              {displayComponent}
              <ControlWidget />
          </div>
    </div>
  );
}

export default App;
