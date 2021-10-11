import React, { useState } from 'react'
import axios from "axios"
import '../../App.css';

function LaserControlWidget(props) {
    const [laserPower, setLaserPower] = useState("10%")
    const [laserState, setLaserState] = useState(false)

    const alterLaserState = () => {
        let newState = !laserState
        setLaserState(newState)
        let cmdURL = props.baseURL + '/laser_state'
        axios.post(cmdURL, { laser_state: newState }).then((response) => {
            console.log(response)
        }).catch((error) => {
            console.log(error)
        });
    }

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
                    <button onClick={alterLaserState} style={laserState ? {backgroundColor:"red",borderRadius:"5px"} : {}}><span>&#9211; Toggle Laser</span></button>
                    {/*<span>
                        <button onClick={() => arrowAlterControl("int", 1)}><span>&#9650;</span></button>
                        <button onClick={() => arrowAlterControl("int", -1)}><span>&#9660;</span></button>
                    </span>
                    <input value={laserPower} style={{ textAlign: 'center', color: '#fff' }} onChange={(e) => alterControl(e.target.value)}></input>*/}
                </div>
            </div>
        </div>
    )
}

export default LaserControlWidget;