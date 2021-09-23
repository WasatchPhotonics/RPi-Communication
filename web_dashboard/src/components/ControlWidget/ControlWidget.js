import React from 'react'
import DetectorControlWidget from './DetectorControlWidget'
import LaserControlWidget from './LaserControlWidget'
import XAxisControlWidget from './XAxisControlWidget'

function ControlWidget(props) {

    return (
        <div className="controlWidget">
            <DetectorControlWidget getSpectra={props.getSpectra} baseURL={props.baseURL} obtainedEEPROM={props.obtainedEEPROM}/>
            <LaserControlWidget baseURL={props.baseURL} />
            <XAxisControlWidget
                markers={props.markers}
                setMarkers={props.setMarkers}
                xUnits={props.xUnits}
                setXUnits={props.setXUnits}
                reverseAxis={props.reverseAxis}
                setReverseAxis={props.setReverseAxis} />
        </div>
        )
}

export default ControlWidget;