import React, { useEffect } from 'react'
import axios from "axios"
import EEPROM0 from './EEPROM0'
import EEPROM1 from './EEPROM1'
import '../../App.css';

function HardwarePage(props) {

    return (
        <div className="displayWindow">
            <div className="container">
                <span style={{textAlign: "left"}}>EEPROM Contents</span>
                <EEPROM0 eeprom={props.eepromFields} setEEPROM={props.setEEPROMFields}/>
                <EEPROM1 eeprom={props.eepromFields} setEEPROM={props.setEEPROMFields}/>
            </div>
        </div>
    );
}

export default HardwarePage;