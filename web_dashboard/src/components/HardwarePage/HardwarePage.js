import React, { useState, useEffect } from 'react'
import axios from "axios"
import EEPROM0 from './EEPROM0'
import '../../App.css';

function parseValue(value) {
    let binNum = 0
    for (let i = 0; i < value.length; i++) {
        binNum += value[i] << (8*i)
    }
    return binNum
}

function parseEEPROM(eeprom) {
    let newState = {}
    let page0 = eeprom[0]
    let model = page0.slice(0, 16).map((int) => {return String.fromCharCode(int)}).join("")
    model = model.replace(/\u0000/g, " ");
    newState["model"] = model
    let sn = page0.slice(16, 32).map((int) => { return String.fromCharCode(int) }).join("")
    sn = sn.replace(/\u0000/g, " ");
    newState["serial_number"] = sn
    newState["baud_rate"] = parseValue(page0.slice(32, 36))
    newState["has_cooling"] = page0[36]
    newState["has_battery"] = page0[37]
    newState["has_laser"] = page0[38]
    let featureMask = parseValue(page0.slice(39,41))
    newState["invert_x_axis"] = Boolean(featureMask & 0x0001)
    newState["bin_2x2"] = Boolean(featureMask & 0x0002)
    newState["gen15"] = Boolean(featureMask & 0x0004)
    newState["cutoff_filter_installed"] = Boolean(featureMask & 0x0008)
    newState["hardware_even_odd"] = Boolean(featureMask & 0x0010)
    newState["excitation_nm_float"] = 785
    newState["slit_size_um"] = parseValue(page0.slice(41, 43))
    newState["startup_integration_time_ms"] = parseValue(page0.slice(43, 45))
    newState["startup_temp_degC"] = parseValue(page0.slice(45, 47))
    newState["startup_triggering_scheme"] = page0[47]
    newState["detector_gain"] = page0.slice(48,52)
    newState["detector_offset"] = page0.slice(52,54)
    newState["detector_gain_odd"] = page0.slice(54,58)
    newState["detector_offset_odd"] = page0.slice(58, 60)
    newState["format"] = page0[63]

    return newState

}

function HardwarePage() {
    const [obtainedEEPROM, setObtainedEEPROM] = useState(false)
    const [eepromFields, setEEPROMFields] = useState({
        "serial_number": "xx",
        "model": "xx",
        "baud_rate": 300,
        "has_cooling": false,
        "has_battery": false,
        "has_laser": false,
        "invert_x_axis": false,
        "bin_2x2": false,
        "gen15": false,
        "cutoff_filter_installed": false,
        "hardware_even_odd": false,
        "excitation_nm_float": 785.0,
        "slit_size_um": 15,
        "startup_integration_time_ms": 400,
        "startup_temp_degC": 15,
        "startup_triggering_scheme": 0,
        "detector_gain": 1,
        "detector_offset": 1,
        "detector_gain_odd": 1,
        "detector_offset_odd": 1,
        "format": 1,
    })

    const baseURL = "http://192.168.1.30:8000"

    const getEEPROM = () => {
        let cmdURL = baseURL + "/eeprom"
        axios.get(cmdURL).then((response) => {
            console.log(response)
            let newEEPROM = parseEEPROM(response.data.Value)
            setEEPROMFields(newEEPROM)
        })
    }

    useEffect(() => {
        if (!obtainedEEPROM) {
            getEEPROM()
            setObtainedEEPROM(true)
        }
    })

    return (
        <div className="displayWindow">
            <div className="container">
                <span style={{textAlign: "left"}}>EEPROM Contents</span>
                <EEPROM0 eeprom={eepromFields} setEEPROM={setEEPROMFields}/>
            </div>
        </div>
    );
}

export default HardwarePage;