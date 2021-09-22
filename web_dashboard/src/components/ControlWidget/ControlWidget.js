import React from 'react'
import DetectorControlWidget from './DetectorControlWidget'
import LaserControlWidget from './LaserControlWidget'

function ControlWidget(props) {

    return (
        <div className="controlWidget">
            <DetectorControlWidget getSpectra={props.getSpectra}/>
            <LaserControlWidget />
        </div>
        )
}

export default ControlWidget;