import React from 'react'
import { LineChart, Line, CartesianGrid, XAxis, YAxis, ResponsiveContainer, Label, Tooltip } from 'recharts';
import '../../App.css';


function SpectraChart(props) {

    const xAxisLabels = {"pixel":"Pixels", "wavelength":"Wavelength (nm)", "wavenumber": "Wavenumber (cm\u207B\u00B9)"}

    // The default tooltip was only showing the x axis. A custom tooltip solved this

    const CustomTooltip = ({ active, payload, label }) => {
        if (active && payload) {
            return (
                <div className="tooltip">
                    <p>x: {label} </p>
                    <p>y: {payload[0].value} </p>
                </div>
            );
        }

        return null;
    };

  return (
      <div className="graphWidget">
          <div className="graphContainer">
            <ResponsiveContainer width="90%" aspect={2} className="graph">
            <LineChart data={props.spectraValues} margin={{ top: 50, right: 50, left: 20, bottom: 20 }}>
                      <Line type="monotone" stroke="#fff" dataKey="count" dot={props.markers} isAnimationActive={false}/>
                      <CartesianGrid horizontal={false} vertical={false}/>
                      <XAxis axisLine={true} interval="preserveStartEnd" dataKey={props.xUnits} reversed={props.reverseAxis}>
                          <Label value={xAxisLabels[props.xUnits]} offset={-10} position="insideBottom" fill='#f0f0f0'/>
                      </XAxis>
                      <YAxis axisLine={true} dataKey="count">
                          <Label value="Count" offset={-10} position="insideLeft" angle={-90} fill='#f0f0f0'/>
                  </YAxis>
                      <Tooltip content={<CustomTooltip />}/>
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