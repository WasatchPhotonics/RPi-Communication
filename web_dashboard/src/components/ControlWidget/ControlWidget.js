import React from 'react'
import DetectorControlWidget from './DetectorControlWidget'
import LaserControlWidget from './LaserControlWidget'

function ControlWidget() {

    return (
        <div className="controlWidget">
            <DetectorControlWidget />
            <LaserControlWidget />
        </div>
        )
}

export default ControlWidget;