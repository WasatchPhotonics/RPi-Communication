import React, { useState, useEffect } from 'react'
import axios from "axios"
import { LineChart, Line, CartesianGrid, XAxis, YAxis } from 'recharts';
import '../App.css';

const baseURL = "http://127.0.0.1:8000"

function SpectraChart() {
  const [spectraValues, setSpectraValues] = useState();

   const getSpectra = () => {
    console.log('performing axios call')
    let spectraUrl = baseURL + '/spectra'
    axios.get(spectraUrl).then((response) => {
      console.log(response)
      if(response.data.Error == null && response.data.Value != null)
      {
        let data = [];
        let i = 0;
        response.data.Value.forEach(element => {
          data.push({"pixel": i, "count": element})
          i += 1;
        });
        setSpectraValues(data);
      }
    })
  }

  return (
    <div>
      <LineChart width="100%" height="100%" data={spectraValues}>
        <Line type="monotone" stroke="#8884d8" dataKey="count"/>
        <CartesianGrid stroke="#fff"/>
        <XAxis dataKey="pixel"/>
        <YAxis />
      </LineChart>
      <button onClick={() => getSpectra()}>Get Spectra</button>
    </div>
  );
}

export default SpectraChart;