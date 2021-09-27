import '../App.css';

function Header(props) {
    const openGithub = () => {
        window.open("https://github.com/WasatchPhotonics/RPi-Communication/tree/main", "_blank");
    }
    return (
        <div className="headerLayout">
            <img src="./enlightenLOGO.png" alt="enlighten logo" style={{ width: "15%", paddingRight: "10px"}} />
            <select onChange={(e) => props.setDisplay(e.target.value)}>
                <option value="scope">Scope</option>
                <option value="hardware">Hardware</option>
            </select>
            <div className="helpButton">
                <button onClick={openGithub}>?</button>
            </div>
        </div>
    );
}

export default Header;