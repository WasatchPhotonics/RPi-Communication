import React, { useState, useEffect } from 'react'
import axios from "axios"
import '../../App.css';


const baseURL = "http://192.168.1.30:8000"

function LaserControlWidget() {
    const [laserPower, setLaserPower] = useState("10%")

    const arrowAlterControl = (direction) => {
    }

    const alterControl = (value) => {
        value.replace("%", "")
        setLaserPower(value);
    }

    return (
        <div>
            <span className="controlTitles">Laser Control</span>
            <div className="controlWidgetContainer">
                <div className="controlInputs">
                    <button><span>&#9211; Toggle Laser</span></button>
                    <span>
                        <button onClick={() => arrowAlterControl("int", 1)}><span>&#9650;</span></button>
                        <button onClick={() => arrowAlterControl("int", -1)}><span>&#9660;</span></button>
                    </span>
                    <input value={laserPower} style={{ textAlign: 'center', color: '#fff' }} onChange={(e) => alterControl(e.target.value)}></input>
                </div>
            </div>
        </div>
    )
}

export default LaserControlWidget;