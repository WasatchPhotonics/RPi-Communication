import React, { useState } from 'react'
import '../../App.css';

function EEPROM1(props) {
    const [authState, setauthState] = useState(true);

    return (
        <div style={{marginBottom:"5px", marginTop:"10px"}}>
                <div className="container">
                    EEPROM Page 1
                    <div className="eepromInput">
                    <input name="wavelength_coeffs[0]" value={props.eeprom["wavelength_coeffs[0]"]} disabled={authState}></input>
                        &nbsp;&nbsp;Wavecal Coeff0
                    </div>
                    <div className="eepromInput">
                    <input name="wavelength_coeffs[1]" value={props.eeprom["wavelength_coeffs[1]"]} disabled={authState}></input>
                        &nbsp;&nbsp;Wavecal Coeff1
                    </div>
                    <div className="eepromInput">
                    <input name="wavelength_coeffs[2]" value={props.eeprom["wavelength_coeffs[2]"]} disabled={authState}></input>
                        &nbsp;&nbsp;Wavecal Coeff2
                    </div>
                    <div className="eepromInput">
                    <input name="wavelength_coeffs[3]" value={props.eeprom["wavelength_coeffs[3]"]} disabled={authState}></input>
                        &nbsp;&nbsp;Wavecal Coeff3
                    </div>
                    <div className="eepromInput">
                    <input name="degC_to_dac_coeffs[0]" value={props.eeprom["degC_to_dac_coeffs[0]"]} disabled={authState}></input>
                        &nbsp;&nbsp;TEC Coeff0 (&#176;C&#8594;DAC)
                    </div>
                    <div className="eepromInput">
                    <input name="degC_to_dac_coeffs[1]" value={props.eeprom["degC_to_dac_coeffs[1]"]} disabled={authState}></input>
                        &nbsp;&nbsp;TEC Coeff1
                    </div>
                    <div className="eepromInput">
                    <input name="degC_to_dac_coeffs[2]" value={props.eeprom["degC_to_dac_coeffs[2]"]} disabled={authState}></input>
                        &nbsp;&nbsp;TEC Coeff2
                    </div>
                    <div className="eepromInput">
                    <input name="max_temp_degC" value={props.eeprom["max_temp_degC"]} type="number" disabled={authState}></input>
                        &nbsp;&nbsp;Max Temp (&#176;C)
                    </div>
                    <div className="eepromInput">
                    <input name="min_temp_degC" value={props.eeprom["min_temp_degC"]} type="number" disabled={authState}></input>
                        &nbsp;&nbsp;Min Temp (&#176;C)
                    </div>
                    <div className="eepromInput">
                    <input name="adc_to_degC_coeffs[0]" value={props.eeprom["adc_to_degC_coeffs[0]"]} disabled={authState}></input>
                        &nbsp;&nbsp;Thermistor Coeff0 (ADC&#8594;&#176;C)
                    </div>
                    <div className="eepromInput">
                    <input name="adc_to_degC_coeffs[1]" value={props.eeprom["adc_to_degC_coeffs[1]"]} disabled={authState}></input>
                        &nbsp;&nbsp;Thermistor Coeff1
                    </div>
                    <div className="eepromInput">
                    <input name="adc_to_degC_coeffs[2]" value={props.eeprom["adc_to_degC_coeffs[2]"]} disabled={authState}></input>
                        &nbsp;&nbsp;Thermistor Coeff2
                    </div>
                    <div className="eepromInput">
                    <input name="tec_r298" value={props.eeprom["tec_r298"]} type="number" disabled={authState}></input>
                        &nbsp;&nbsp;Thermistor Resistance at 298K
                    </div>
                    <div className="eepromInput">
                    <input name="tec_beta" value={props.eeprom["tec_beta"]} type="number" disabled={authState}></input>
                        &nbsp;&nbsp;Thermistor Beta Value
                    </div>
                    <div className="eepromInput">
                    <input name="calibration_date" value={props.eeprom["calibration_date"]} disabled={authState}></input>
                        &nbsp;&nbsp;Calibration Date
                    </div>
                    <div className="eepromInput">
                    <input name="calibrated_by" value={props.eeprom["calibrated_by"]} disabled={authState}></input>
                        &nbsp;&nbsp;Calibration By
                    </div>
                </div>
            </div>
    );
}

export default EEPROM1;