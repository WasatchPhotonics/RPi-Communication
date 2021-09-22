import SpectraChart from './Chart';
import Marquee from './Marquee'
import '../../App.css';

function ScopePage() {
    return (
        <div className="displayWindow">
            <Marquee />
            <div className="pageWindow">
                <SpectraChart />
            </div>
        </div>
    );
}

export default ScopePage;