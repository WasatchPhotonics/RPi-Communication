import React, { useState, useEffect } from 'react'
import axios from "axios"
import { LineChart, Line, CartesianGrid, XAxis, YAxis, ResponsiveContainer, Label } from 'recharts';
import '../../App.css';

const baseURL = "http://192.168.1.30:8000"

function SpectraChart(props) {


  return (
      <div className="graphWidget">
          <div className="graphContainer">
            <ResponsiveContainer width="90%" aspect={2} className="graph">
            <LineChart data={props.spectraValues} margin={{ top: 50, right: 50, left: 20, bottom: 20 }}>
                      <Line type="monotone" stroke="#fff" dataKey="count" dot={false} isAnimationActive={false}/>
                      <CartesianGrid horizontal={false} vertical={false}/>
                      <XAxis axisLine={true} interval="preserveStartEnd">
                      <Label value="Pixels" offset={-10} position="insideBottom" fill='#f0f0f0'/>
                  </XAxis>
                      <YAxis axisLine={true}>
                          <Label value="Count" offset={-10} position="insideLeft" angle={-90} fill='#f0f0f0'/>
                  </YAxis>
            </LineChart>
            </ResponsiveContainer>
          </div>
          <div className="container">
              Max: {props.spectraStats["max"].toFixed(2)}&nbsp;&nbsp;&nbsp;
              Min: {props.spectraStats["min"].toFixed(2)}&nbsp;&nbsp;&nbsp;
              Mean: {props.spectraStats["mean"].toFixed(2)}&nbsp;&nbsp;&nbsp;
          </div>
    </div>
  );
}

export default SpectraChart;