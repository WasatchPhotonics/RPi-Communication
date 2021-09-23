import React, { useState, useEffect } from 'react'
import ScopePage from './components/ScopePage/ScopePage'
import ControlWidget from './components/ControlWidget/ControlWidget'
import Header from './components/Header'
import axios from 'axios'
import './App.css';
import HardwarePage from './components/HardwarePage/HardwarePage';

function parseValue(value) {
    let binNum = 0
    for (let i = 0; i < value.length; i++) {
        binNum += value[i] << (8 * i)
    }
    return binNum
}

function parseFloatValue(value) {
    // https://stackoverflow.com/questions/52106570/javascript-convert-bytes-into-float-in-a-clean-way
    // This took some digging. Essentially I see this similar to how we used a union in fw
    // the buffer is shared between bytes and float and returning float returns it as a Javascript
    // floating point number
    let buffer = new ArrayBuffer(4);
    let bytes = new Uint8Array(buffer);
    let float = new Float32Array(buffer);
    for (let i = 0; i < value.length; i++) {
        bytes[i] = value[i]
    }
    let result = float.toString()
    result = parseFloat(result)
    return result
}

function parseEEPROM(eeprom) {
    let newState = {}
    let page0 = eeprom[0]
    let page1 = eeprom[1]
    let page2 = eeprom[2]
    let page3 = eeprom[3]
    let page4 = eeprom[4]
    let model = page0.slice(0, 16).map((int) => { return String.fromCharCode(int) }).join("")
    model = model.replace(/\u0000/g, " ");
    newState["model"] = model
    let sn = page0.slice(16, 32).map((int) => { return String.fromCharCode(int) }).join("")
    sn = sn.replace(/\u0000/g, " ");
    newState["serial_number"] = sn
    newState["baud_rate"] = parseValue(page0.slice(32, 36))
    newState["has_cooling"] = page0[36]
    newState["has_battery"] = page0[37]
    newState["has_laser"] = page0[38]
    let featureMask = parseValue(page0.slice(39, 41))
    newState["invert_x_axis"] = Boolean(featureMask & 0x0001)
    newState["bin_2x2"] = Boolean(featureMask & 0x0002)
    newState["gen15"] = Boolean(featureMask & 0x0004)
    newState["cutoff_filter_installed"] = Boolean(featureMask & 0x0008)
    newState["hardware_even_odd"] = Boolean(featureMask & 0x0010)
    newState["excitation_nm_float"] = parseFloatValue(page3.slice(36, 40)) //page3 but gui in enlighten isn't updated either
    newState["slit_size_um"] = parseValue(page0.slice(41, 43))
    newState["startup_integration_time_ms"] = parseValue(page0.slice(43, 45))
    newState["startup_temp_degC"] = parseValue(page0.slice(45, 47))
    newState["startup_triggering_scheme"] = page0[47]
    newState["detector_gain"] = parseFloatValue(page0.slice(48, 52)).toFixed(2)
    newState["detector_offset"] = parseValue(page0.slice(52, 54))
    newState["detector_gain_odd"] = parseFloatValue(page0.slice(54, 58)).toFixed(2)
    newState["detector_offset_odd"] = parseValue(page0.slice(58, 60))
    newState["format"] = page0[63]

    newState["wavelength_coeffs[0]"] = parseFloatValue(page1.slice(0, 4))
    newState["wavelength_coeffs[1]"] = parseFloatValue(page1.slice(4, 8))
    newState["wavelength_coeffs[2]"] = parseFloatValue(page1.slice(8, 12))
    newState["wavelength_coeffs[3]"] = parseFloatValue(page1.slice(12, 16))
    newState["degC_to_dac_coeffs[0]"] = parseFloatValue(page1.slice(16, 20))
    newState["degC_to_dac_coeffs[1]"] = parseFloatValue(page1.slice(20, 24))
    newState["degC_to_dac_coeffs[2]"] = parseFloatValue(page1.slice(24, 28))
    newState["max_temp_degC"] = parseValue(page1.slice(28, 30))
    newState["min_temp_degC"] = parseValue(page1.slice(30, 32))
    newState["adc_to_degC_coeffs[0]"] = parseFloatValue(page1.slice(32, 36)).toFixed(2)
    newState["adc_to_degC_coeffs[1]"] = parseFloatValue(page1.slice(36, 40)).toFixed(2)
    newState["adc_to_degC_coeffs[2]"] = parseFloatValue(page1.slice(40, 44)).toFixed(2)
    newState["tec_r298"] = parseValue(page1.slice(44, 46))
    newState["tec_beta"] = parseValue(page1.slice(46, 48))
    let calibDate = page1.slice(48, 60).map((int) => { return String.fromCharCode(int) }).join("")
    calibDate = calibDate.replace(/\u0000/g, " ")
    newState["calibration_date"] = calibDate
    let calibBy = page1.slice(60, 63).map((int) => { return String.fromCharCode(int) }).join("")
    calibBy = calibBy.replace(/\u0000/g, " ")
    newState["calibrated_by"] = calibBy


    return newState

}
function App() {
    const [display, setDisplay] = useState("scope");
    const [markers, setMarkers] = useState(false);
    const [reverseAxis, setReverseAxis] = useState(false);
    const [xUnits, setXUnits] = useState("pixel");
    const [obtainedEEPROM, setObtainedEEPROM] = useState(false)
    const [spectraValues, setSpectraValues] = useState();
    const [spectraStats, setSpectraStats] = useState({
        "max": 0,
        "min": 0,
        "mean":0,
    })
    var displayComponent;
    // This is not the prettiest way to do this, but I don't want to take
    // the time yet to create a redux store with reducers, actions etc.
    const [eepromFields, setEEPROMFields] = useState({
        "serial_number": "XX",
        "model": "XX",
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

        "wavelength_coeffs[0]": 1,
        "wavelength_coeffs[1]": 1,
        "wavelength_coeffs[2]": 1,
        "wavelength_coeffs[3]": 1,
        "degC_to_dac_coeffs[0]": 1,
        "degC_to_dac_coeffs[1]": 1,
        "degC_to_dac_coeffs[2]": 1,
        "max_temp_degC": 1,
        "min_temp_degC": 1,
        "adc_to_degC_coeffs[0]": 1,
        "adc_to_degC_coeffs[1]": 1,
        "adc_to_degC_coeffs[2]": 1,
        "tec_r298": 1,
        "tec_beta": 1,
        "calibration_date": 1,
        "calibrated_by": "XX",
    })

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

    const baseURL = "http://192.168.1.30:8000"

    const getSpectra = () => {
        console.log('performing axios call')
        let spectraUrl = baseURL + '/spectra'
        let max = 0
        let min = Infinity
        let mean = 0
        axios.get(spectraUrl).then((response) => {
            console.log(response)
            if (response.data.Error == null && response.data.Value != null) {
                let data = new Array(response.data.Value.length).fill(0);
                let i = 1;
                response.data.Value.forEach(element => {
                    if (element > max) { max = element }
                    if (element < min) { min = element }
                    let nm = eepromFields["wavelength_coeffs[0]"] + 
                        eepromFields["wavelength_coeffs[1]"] * i + 
                        eepromFields["wavelength_coeffs[2]"] * i * i +
                        eepromFields["wavelength_coeffs[3]"] * i * i * i
                    let waveNum = (1e7 / eepromFields["excitation_nm_float"]) - (1e7 / nm);
                    mean += element
                    data[i] = { "pixel": i, "count": element, "wavelength": nm.toFixed(2), "wavenumber": waveNum.toFixed(2)}
                    i += 1;
                });
                mean /= response.data.Value.length
                setSpectraValues(data);
                setSpectraStats({"max": max, "min": min, "mean": mean})
            }
        })
    }

    if (display === "scope") {
        displayComponent = <ScopePage spectraValues={spectraValues}
            spectraStats={spectraStats}
            baseURL={baseURL}
            reverseAxis={reverseAxis}
            xUnits={xUnits}
            markers={markers}/>
    }
    else if (display === "hardware") {
        displayComponent = <HardwarePage baseURL={baseURL}
            setEEPROMFields={setEEPROMFields}
            eepromFields={eepromFields}
            obtainedEEPROM={obtainedEEPROM}
            setObtainedEEPROM={setObtainedEEPROM}/>
    }



  return (
      <div className="App">
          <Header setDisplay={ setDisplay }/>
          <div className="appWindow">
              {displayComponent}
              <ControlWidget getSpectra={getSpectra}
                  baseURL={baseURL}
                  obtainedEEPROM={obtainedEEPROM}
                  markers={markers}
                  setMarkers={setMarkers}
                  xUnits={xUnits}
                  setXUnits={setXUnits}
                  reverseAxis={reverseAxis}
                  setReverseAxis={setReverseAxis}/>
          </div>
    </div>
  );
}

export default App;
