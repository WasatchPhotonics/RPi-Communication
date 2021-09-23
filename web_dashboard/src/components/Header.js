import '../App.css';

function Header(props) {
    return (
        <div className="headerLayout">
            <img src="./enlightenLOGO.png" alt="enlighten logo" style={{ width: "15%", paddingRight: "10px"}} />
            <select onChange={(e) => props.setDisplay(e.target.value)}>
                <option value="scope">Scope</option>
                <option value="hardware">Hardware</option>
            </select>
        </div>
    );
}

export default Header;