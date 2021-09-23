import React from 'react'
import '../../App.css';



function XAxisControlWidget(props) {

    return (
        <div>
            <span className="controlTitles">X Axis</span>
            <div className="controlWidgetContainer">
                <select onChange={(e) => props.setXUnits(e.target.value)}>
                    <option value="pixel">Pixels</option>
                    <option value="wavelength">Wavelength</option>
                    <option value="wavenumber">Wavenumber</option>
                </select>
                <div className="controlInputs">
                    <div style={{display:"flex"}}>
                        <input type="checkbox" checked={props.markers} onClick={() => props.setMarkers(!props.markers)}></input>Show Markers
                    </div>
                    <div style={{display:"flex"}}>
                        <input type="checkbox" checked={props.reverseAxis} onClick={() => props.setReverseAxis(!props.reverseAxis)}></input>Invert X Axis
                    </div>
                </div>
            </div>
        </div>
    )
}

export default XAxisControlWidget;