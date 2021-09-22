import '../App.css';

function Header() {
    return (
        <div className="headerLayout">
            <img src="/enlightenLOGO.png" alt="enlighten logo" style={{ width: "15%", paddingRight: "10px"}} />
            <select>
                <option value="scope">Scope</option>
                <option value="hardware">Hardware</option>
            </select>
        </div>
    );
}

export default Header;