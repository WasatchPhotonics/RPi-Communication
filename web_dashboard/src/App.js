import React, { useState, useEffect } from 'react'
import ScopePage from './components/ScopePage/ScopePage'
import ControlWidget from './components/ControlWidget/ControlWidget'
import Header from './components/Header'
import axios from 'axios'
import './App.css';
import HardwarePage from './components/HardwarePage/HardwarePage';

function App() {
    const [display, setDisplay] = useState("scope");
    const [spectraValues, setSpectraValues] = useState();
    const [spectraStats, setSpectraStats] = useState({
        "max": 0,
        "min": 0,
        "mean":0,
    })
    var displayComponent;

    const baseURL = "http://192.168.1.30:8000"

    const getSpectra = () => {
        console.log('performing axios call')
        let spectraUrl = baseURL + '/spectra'
        let max = 0
        let min = Infinity
        let mean = 0
        axios.get(spectraUrl).then((response) => {
            console.log(response)
            if (response.data.Error == null && response.data.Value != null) {
                let data = [];
                let i = 1;
                response.data.Value.forEach(element => {
                    if (element > max) { max = element }
                    if (element < min) { min = element }
                    mean += element
                    data.push({ "pixel": i, "count": element })
                    i += 1;
                });
                mean /= response.data.Value.length
                setSpectraValues(data);
                setSpectraStats({"max": max, "min": min, "mean": mean})
            }
        })
    }

    if (display == "scope") {
        displayComponent = <ScopePage spectraValues={spectraValues} spectraStats={spectraStats}/>
    }
    else if (display == "hardware") {
        displayComponent = <HardwarePage />
    }



  return (
      <div className="App">
          <Header setDisplay={ setDisplay }/>
          <div className="appWindow">
              {displayComponent}
              <ControlWidget getSpectra={getSpectra}/>
          </div>
    </div>
  );
}

export default App;
