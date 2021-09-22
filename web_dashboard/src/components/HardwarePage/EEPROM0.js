import React, { useState, useEffect } from 'react'
import '../../App.css';

function EEPROM0(props) {
    const [authState, setauthState] = useState(true);

    return (
            <div>
                <div className="container">
                    EEPROM Page 0
                    <div className="eepromInput">
                    <input name="serial_number" value={props.eeprom["serial_number"]} disabled={authState}></input>
                        &nbsp;&nbsp;Serial Number
                    </div>
                    <div className="eepromInput">
                    <input name="model" value={props.eeprom["model"]} disabled={authState}></input>
                        &nbsp;&nbsp;Model
                    </div>
                    <div className="eepromInput">
                    <input name="baud_rate" value={props.eeprom["baud_rate"]} type="number" disabled={authState}></input>
                        &nbsp;&nbsp;Baud Rate
                    </div>
                    <div className="eepromInput">
                    <input name="has_cooling" checked={props.eeprom["has_cooling"]} type="checkbox" disabled={authState}></input>
                        &nbsp;&nbsp;Cooling Available
                    </div>
                    <div className="eepromInput">
                    <input name="has_battery" checked={props.eeprom["has_battery"]} type="checkbox" disabled={authState}></input>
                        &nbsp;&nbsp;Battery Available
                    </div>
                    <div className="eepromInput">
                    <input name="has_laser" checked={props.eeprom["has_laser"]} type="checkbox" disabled={authState}></input>
                        &nbsp;&nbsp;Laser Available
                    </div>
                    <div className="eepromInput">
                    <input name="invert_x_axis" checked={props.eeprom["invert_x_axis"]} type="checkbox" disabled={authState}></input>
                        &nbsp;&nbsp;Invert X-Axis
                    </div>
                    <div className="eepromInput">
                    <input name="bin_2x2" checked={props.eeprom["bin_2x2"]} type="checkbox" disabled={authState}></input>
                        &nbsp;&nbsp;Bin 2x2
                    </div>
                    <div className="eepromInput">
                    <input name="gen15" checked={props.eeprom["gen15"]} type="checkbox" disabled={authState}></input>
                        &nbsp;&nbsp;Gen 1.5
                    </div>
                    <div className="eepromInput">
                    <input name="cutoff_filter_installed" checked={props.eeprom["cutoff_filter_installed"]} type="checkbox" disabled={authState}></input>
                        &nbsp;&nbsp;Cutoff Filter Installed
                    </div>
                    <div className="eepromInput">
                    <input name="hardware_even_odd" checked={props.eeprom["hardware_even_odd"]} type="checkbox" disabled={authState}></input>
                        &nbsp;&nbsp;Hardware Even/Odd Correction
                    </div>
                    <div className="eepromInput">
                    <input name="excitation_nm_float" value={props.eeprom["excitation_nm_float"]} type="number" disabled={authState}></input>
                        &nbsp;&nbsp;Excitation (nm)
                    </div>
                    <div className="eepromInput">
                    <input name="slit_size_um" value={props.eeprom["slit_size_um"]} type="number" disabled={authState}></input>
                        &nbsp;&nbsp;Slit Size (um)
                    </div>
                    <div className="eepromInput">
                    <input name="startup_integration_time_ms" value={props.eeprom["startup_integration_time_ms"]} type="number" disabled={authState}></input>
                        &nbsp;&nbsp;Startup Integration Time(ms)
                    </div>
                    <div className="eepromInput">
                    <input name="startup_temp_degC" value={props.eeprom["startup_temp_degC"]} type="number" disabled={authState}></input>
                        &nbsp;&nbsp;Startup Detector Temp (C)
                    </div>
                    <div className="eepromInput">
                    <input name="startup_triggering_scheme" value={props.eeprom["startup_triggering_scheme"]} type="number" disabled={authState}></input>
                        &nbsp;&nbsp;Startup Triggering Scheme
                    </div>
                    <div className="eepromInput">
                    <input name="detector_gain" value={props.eeprom["detector_gain"]} type="number" disabled={authState}></input>
                        &nbsp;&nbsp;Detector Gain (InGaAs even)
                    </div>
                    <div className="eepromInput">
                    <input name="detector_offset" value={props.eeprom["detector_offset"]} type="number" disabled={authState}></input>
                        &nbsp;&nbsp;Detector Offset (InGaAs even)
                    </div>
                    <div className="eepromInput">
                    <input name="detector_gain_odd" value={props.eeprom["detector_gain_odd"]} type="number" disabled={authState}></input>
                        &nbsp;&nbsp;Detector Gain (InGaAs odd)
                    </div>
                    <div className="eepromInput">
                    <input name="detector_offset_odd" value={props.eeprom["detector_offset_odd"]} type="number" disabled={authState}></input>
                        &nbsp;&nbsp;Detector Offset (InGaAs odd)
                    </div>
                    <div className="eepromInput">
                    <input name="format" value={props.eeprom["format"]} disabled={authState}></input>
                        &nbsp;&nbsp;format
                    </div>

                </div>
            </div>
    );
}

export default EEPROM0;