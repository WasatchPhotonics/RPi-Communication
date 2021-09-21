import React, { useState, useEffect } from 'react'
import axios from "axios"
import { LineChart, Line, CartesianGrid, XAxis, YAxis, ResponsiveContainer, Label } from 'recharts';
import '../App.css';

const baseURL = "http://192.168.1.30:8000"

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
          <div className="graphContainer">
            <ResponsiveContainer width="90%" aspect={1.5} className="graph">
            <LineChart data={spectraValues} margin={{ top: 50, right: 50, left: 20, bottom: 20 }}>
                      <Line type="monotone" stroke="#fff" dataKey="count" dot={false}/>
                      <CartesianGrid horizontal={false} vertical={false}/>
                      <XAxis axisLine={true}>
                      <Label value="Pixels" offset={-10} position="insideBottom" fill='#f0f0f0'/>
                  </XAxis>
                      <YAxis axisLine={true}>
                          <Label value="Count" offset={-10} position="insideLeft" angle={-90} fill='#f0f0f0'/>
                  </YAxis>
          </LineChart>
          </ResponsiveContainer>
          </div>
      <button onClick={() => getSpectra()}>Get Spectra</button>
    </div>
  );
}

export default SpectraChart;