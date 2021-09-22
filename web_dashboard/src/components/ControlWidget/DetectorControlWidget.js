import React, { useState, useEffect } from 'react'
import axios from "axios"
import '../../App.css';


const baseURL = "http://192.168.1.30:8000"

function DetectorControlWidget(props) {
    const [intTime, setIntTime] = useState("10")
    const [gain, setGain] = useState("5")

    const arrowAlterControl = (setting, direction) => {
        if(setting == "gain")
        {
            let res = parseFloat(gain) + direction
            let cmdURL = baseURL + '/gain'
            axios.post(cmdURL, { gain: res }).then((response) => {
                console.log(response)
            }).catch((error) => {
                console.log(error)
            });
            setGain(res.toString())
        }
        else
        {
            let res = parseFloat(intTime) + direction 
            let cmdURL = baseURL + '/int'
            axios.post(cmdURL, { int_time: res }).then((response) => {
                console.log(response)
            }).catch((error) => {
                console.log(error)
            });
            setIntTime(res.toString())
        }
    }

    const alterControl = (setting, value) => {
        if (setting == "gain")
        {
            setGain(value)
        }
        else
        {
            setIntTime(value)
        }
    }

    return (
        <div>
            <span className="controlTitles">Detector Control</span>
            <div className="controlWidgetContainer">
                <div className="controlInputs">
                    <span>Integartion Time</span>
                    <span>
                        <button onClick={() => arrowAlterControl("int",1)}><span>&#9650;</span></button>
                        <button onClick={() => arrowAlterControl("int",-1)}><span>&#9660;</span></button>
                    </span>
                    <input value={intTime} style={{ textAlign: 'center', color: '#fff' }} onChange={(e) => alterControl("int",e.target.value)}></input>
                    <button onClick={props.getSpectra}>Get Spectra</button>
                </div>
                <div className="controlInputs">
                    <span>Gain</span>
                    <span>
                        <button onClick={() => arrowAlterControl("gain",1)}><span>&#9650;</span></button>
                        <button onClick={() => arrowAlterControl("gain",-1)}><span>&#9660;</span></button>
                    </span>
                    <input value={gain} style={{ textAlign: 'center', color: '#fff' }} onChange={(e) => alterControl("gain",e.target.value)}></input>
                </div>
            </div>
        </div>
    )
}

export default DetectorControlWidget;